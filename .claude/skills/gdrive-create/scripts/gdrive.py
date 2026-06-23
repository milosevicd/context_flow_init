#!/usr/bin/env python3
"""
gdrive.py — create Google Docs/Sheets and upload files to Google Drive
using a *domain-wide-delegated* (DWD) service account that impersonates a
real user.

Why this exists:
  The project's google-drive MCP server can edit existing files but does
  not create them. This helper creates them. It authenticates with a
  service account that has domain-wide delegation enabled and impersonates
  a real user (GOOGLE_USER_EMAIL). Because the file is created *as that
  user* — who has normal Drive storage quota — creation succeeds and the
  file lands in that user's own Drive. No file-sharing step is needed.

This script does NOT run a browser/auth flow and never mints or stores
long-lived user credentials. It signs a short-lived JWT with the service
account's private key and exchanges it for an access token. If the key or
the impersonation target is missing it stops and tells the user.

Pure Python standard library only — no pip installs required. (RS256 JWT
signing is implemented directly: a tiny DER parser extracts the RSA key
and pow() does the modular exponentiation.)

Subcommands:
  create-doc    Create an empty Google Doc in a folder.
  create-sheet  Create an empty Google Spreadsheet in a folder.
  upload        Upload an existing local file (any format) to a folder,
                optionally converting it to a Google Doc/Sheet.

Configuration is entirely via environment variables:
  GOOGLE_DWD_SVC_ACCT_PK_PATH  Path to the service-account JSON key. The
                               service account must have domain-wide
                               delegation enabled and be authorized for the
                               Drive scope.
  GOOGLE_USER_EMAIL            The user to impersonate. Files are created in
                               this user's Drive.

All commands print a single JSON object on stdout on success.
"""

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

TOKEN_URI = "https://oauth2.googleapis.com/token"
DRIVE_FILES = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"

DOC_MIME = "application/vnd.google-apps.document"
SHEET_MIME = "application/vnd.google-apps.spreadsheet"

SCOPE = "https://www.googleapis.com/auth/drive"


def die(msg):
    print(json.dumps({"ok": False, "error": str(msg)}), file=sys.stdout)
    sys.exit(1)


def validate_folder(folder):
    """Reject empty folders and the Drive 'root' alias.

    The Drive API treats 'root' as a special alias for the user's My Drive
    root. Creating there clutters the top level and is hard to find/clean up,
    so this skill forbids it: a real folder ID must always be supplied.
    """
    if not folder or not folder.strip():
        die("A destination folder ID is required.")
    if folder.strip().lower() == "root":
        die("Refusing to create in the Drive root: 'root' is the special "
            "My Drive alias and is not allowed. Pass a real folder ID "
            "(the token in a folder URL: .../folders/<FOLDER_ID>).")


def http_json(method, url, token=None, headers=None, data=None):
    """Make a JSON HTTP request and return the parsed response."""
    hdrs = {"Accept": "application/json"}
    if token:
        hdrs["Authorization"] = "Bearer " + token
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        die("HTTP %s on %s %s: %s" % (e.code, method, url, detail))
    except urllib.error.URLError as e:
        die("Network error on %s %s: %s" % (method, url, e.reason))


# --------------------------------------------------------------- RS256 / JWT

def _b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _read_len(der, i):
    first = der[i]
    i += 1
    if first < 0x80:
        return first, i
    num = first & 0x7F
    length = int.from_bytes(der[i:i + num], "big")
    return length, i + num


def _read_tlv(der, i):
    """Return (tag, value_bytes, next_index) for one DER TLV element."""
    tag = der[i]
    i += 1
    length, i = _read_len(der, i)
    return tag, der[i:i + length], i + length


def _read_int(der, i):
    tag, value, i = _read_tlv(der, i)
    if tag != 0x02:
        die("Malformed private key: expected INTEGER in DER.")
    return int.from_bytes(value, "big"), i


def _parse_rsa_private_key(pem):
    """Extract (n, e, d) from a PEM RSA private key (PKCS#8 or PKCS#1)."""
    is_pkcs1 = "BEGIN RSA PRIVATE KEY" in pem
    b64 = "".join(line.strip() for line in pem.strip().splitlines()
                  if not line.startswith("-----"))
    der = base64.b64decode(b64)

    if is_pkcs1:
        rsa_der = der
    else:
        # PKCS#8 PrivateKeyInfo SEQUENCE -> unwrap to inner RSAPrivateKey.
        _, info, _ = _read_tlv(der, 0)          # outer SEQUENCE contents
        i = 0
        _, i = _read_int(info, i)               # version
        _, _, i = _read_tlv(info, i)            # privateKeyAlgorithm SEQUENCE
        _, rsa_der, _ = _read_tlv(info, i)      # privateKey OCTET STRING body

    _, seq, _ = _read_tlv(rsa_der, 0)           # RSAPrivateKey SEQUENCE
    j = 0
    _, j = _read_int(seq, j)                    # version
    n, j = _read_int(seq, j)                    # modulus
    e, j = _read_int(seq, j)                    # publicExponent
    d, j = _read_int(seq, j)                    # privateExponent
    return n, e, d


# DigestInfo prefix for SHA-256 (RFC 8017).
_SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


def _rsa_sign_sha256(message, n, d):
    """RSASSA-PKCS1-v1_5 signature over SHA-256(message)."""
    k = (n.bit_length() + 7) // 8
    t = _SHA256_PREFIX + hashlib.sha256(message).digest()
    ps_len = k - len(t) - 3
    if ps_len < 8:
        die("RSA key is too small to sign.")
    em = b"\x00\x01" + b"\xff" * ps_len + b"\x00" + t
    sig_int = pow(int.from_bytes(em, "big"), d, n)
    return sig_int.to_bytes(k, "big")


def _signed_jwt(sa, user_email):
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claims = {
        "iss": sa["client_email"],
        "sub": user_email,          # impersonation target (DWD)
        "scope": SCOPE,
        "aud": TOKEN_URI,
        "iat": now,
        "exp": now + 3600,
    }
    n, _e, d = _parse_rsa_private_key(sa["private_key"])
    signing_input = (
        _b64url(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + _b64url(json.dumps(claims, separators=(",", ":")).encode())
    )
    sig = _rsa_sign_sha256(signing_input.encode("ascii"), n, d)
    return signing_input + "." + _b64url(sig)


# ---------------------------------------------------------------- credentials

def _load_sa():
    sa_path = os.environ.get("GOOGLE_DWD_SVC_ACCT_PK_PATH")
    if not sa_path:
        die("GOOGLE_DWD_SVC_ACCT_PK_PATH is not set — point it at the "
            "domain-wide-delegated service-account JSON key.")
    if not os.path.exists(sa_path):
        die("GOOGLE_DWD_SVC_ACCT_PK_PATH points to a missing file: %s" % sa_path)
    try:
        with open(sa_path, "r", encoding="utf-8") as f:
            sa = json.load(f)
    except Exception as e:
        die("Could not read service account JSON at %s: %s" % (sa_path, e))
    if not sa.get("client_email") or not sa.get("private_key"):
        die("Service account JSON at %s is missing client_email/private_key."
            % sa_path)
    return sa


def access_token():
    """Return a fresh access token via the JWT-bearer (DWD) grant.

    Signs a short-lived assertion with the service account key and exchanges
    it for a token scoped to the impersonated user. Never runs an auth flow.
    """
    sa = _load_sa()
    user_email = os.environ.get("GOOGLE_USER_EMAIL")
    if not user_email:
        die("GOOGLE_USER_EMAIL is not set — set it to the user the service "
            "account should impersonate (domain-wide delegation).")
    assertion = _signed_jwt(sa, user_email)
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    }).encode()
    resp = http_json("POST", TOKEN_URI, headers={
        "Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if "access_token" not in resp:
        die("Token endpoint returned no access_token: %s" % json.dumps(resp))
    return resp["access_token"]


# ------------------------------------------------------------------ create

def create_native(args, mime, kind):
    validate_folder(args.folder)
    token = access_token()
    body = json.dumps({
        "name": args.name,
        "mimeType": mime,
        "parents": [args.folder],
    }).encode()
    url = "%s?fields=id,name,webViewLink,parents&supportsAllDrives=true" % DRIVE_FILES
    resp = http_json("POST", url, token=token, headers={
        "Content-Type": "application/json"}, data=body)
    out = {"ok": True, "action": "create-%s" % kind,
           "id": resp.get("id"), "name": resp.get("name"),
           "webViewLink": resp.get("webViewLink")}
    print(json.dumps(out))


def cmd_create_doc(args):
    create_native(args, DOC_MIME, "doc")


def cmd_create_sheet(args):
    create_native(args, SHEET_MIME, "sheet")


# ------------------------------------------------------------------ upload

def cmd_upload(args):
    validate_folder(args.folder)
    token = access_token()
    if not os.path.exists(args.file):
        die("File not found: %s" % args.file)

    name = args.name or os.path.basename(args.file)
    source_mime = (mimetypes.guess_type(args.file)[0]
                   or "application/octet-stream")

    metadata = {"name": name, "parents": [args.folder]}
    if args.convert == "doc":
        metadata["mimeType"] = DOC_MIME
    elif args.convert == "sheet":
        metadata["mimeType"] = SHEET_MIME
    # else: keep source format (no target mimeType => stored as-is)

    with open(args.file, "rb") as f:
        media = f.read()

    boundary = "----gdrive-boundary-7c3a9f"
    parts = []
    parts.append(("--" + boundary).encode())
    parts.append(b"Content-Type: application/json; charset=UTF-8")
    parts.append(b"")
    parts.append(json.dumps(metadata).encode())
    parts.append(("--" + boundary).encode())
    parts.append(("Content-Type: " + source_mime).encode())
    parts.append(b"")
    body = b"\r\n".join(parts) + b"\r\n" + media + ("\r\n--%s--\r\n" % boundary).encode()

    url = ("%s?uploadType=multipart&fields=id,name,webViewLink&supportsAllDrives=true"
           % DRIVE_UPLOAD)
    resp = http_json("POST", url, token=token, headers={
        "Content-Type": "multipart/related; boundary=%s" % boundary,
        "Content-Length": str(len(body)),
    }, data=body)

    out = {"ok": True, "action": "upload",
           "id": resp.get("id"), "name": resp.get("name"),
           "webViewLink": resp.get("webViewLink")}
    print(json.dumps(out))


# -------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(
        description="Create/upload to Google Drive via a DWD service account.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("create-doc")
    sp.add_argument("--name", required=True)
    sp.add_argument("--folder", required=True, help="Destination folder ID.")
    sp.set_defaults(func=cmd_create_doc)

    sp = sub.add_parser("create-sheet")
    sp.add_argument("--name", required=True)
    sp.add_argument("--folder", required=True, help="Destination folder ID.")
    sp.set_defaults(func=cmd_create_sheet)

    sp = sub.add_parser("upload")
    sp.add_argument("--file", required=True, help="Local file path.")
    sp.add_argument("--folder", required=True, help="Destination folder ID.")
    sp.add_argument("--name", help="Name in Drive (default: source filename).")
    sp.add_argument("--convert", choices=["doc", "sheet"],
                    help="Convert to a native Google Doc/Sheet on upload.")
    sp.set_defaults(func=cmd_upload)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
