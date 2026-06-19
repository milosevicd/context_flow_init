#!/usr/bin/env python3
"""
gdrive.py — create Google Docs/Sheets and upload files to Google Drive
as a *real user* (OAuth), complementing the service-account MCP server.

Why this exists:
  The project's google-drive MCP server authenticates with a service
  account. Service accounts have no personal Drive storage quota, so
  files.create fails with "storageQuotaExceeded" in a normal (My Drive)
  folder. This helper authenticates as a real user (OAuth client id /
  secret + refresh token), so it CAN create files, and always shares
  each new file with the service account so the MCP can then edit it.

This script does NOT mint credentials. Acquiring a refresh token is a
one-time human setup step done outside the skill. If the
refresh token is missing the script stops and tells the user — it never
launches a browser or runs an auth flow.

Pure Python standard library only — no pip installs required.

Subcommands:
  create-doc    Create an empty Google Doc in a folder.
  create-sheet  Create an empty Google Spreadsheet in a folder.
  upload        Upload an existing local file (any format) to a folder,
                optionally converting it to a Google Doc/Sheet.

Configuration is entirely via environment variables:
  GOOGLE_OAUTH_CLIENT_ID       OAuth client id (real-user credentials).
  GOOGLE_OAUTH_CLIENT_SECRET   OAuth client secret.
  GOOGLE_OAUTH_REFRESH_TOKEN   OAuth refresh token (obtained once, externally).
  GOOGLE_SVC_ACCT_PK_PATH      Path to the service-account JSON (the same
                               env var the MCP uses). Every new file is
                               shared with its client_email so the MCP can
                               edit it immediately.

All commands print a single JSON object on stdout on success.
"""

import argparse
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

TOKEN_URI = "https://oauth2.googleapis.com/token"
DRIVE_FILES = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"

DOC_MIME = "application/vnd.google-apps.document"
SHEET_MIME = "application/vnd.google-apps.spreadsheet"


def die(msg):
    print(json.dumps({"ok": False, "error": str(msg)}), file=sys.stdout)
    sys.exit(1)


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


# ---------------------------------------------------------------- credentials

def access_token():
    """Return a fresh access token by exchanging the refresh token.

    All credentials come from the environment. This script never mints a
    refresh token; if one is missing it stops and tells the user.
    """
    cid = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    if not cid or not secret:
        die("Missing client id/secret. Set GOOGLE_OAUTH_CLIENT_ID and "
            "GOOGLE_OAUTH_CLIENT_SECRET.")
    refresh = os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN")
    if not refresh:
        die("No refresh token. Obtain one once and set "
            "GOOGLE_OAUTH_REFRESH_TOKEN. This skill does not run an auth flow.")
    data = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": secret,
        "refresh_token": refresh,
        "grant_type": "refresh_token",
    }).encode()
    resp = http_json("POST", TOKEN_URI, headers={
        "Content-Type": "application/x-www-form-urlencoded"}, data=data)
    return resp["access_token"]


# ----------------------------------------------------------------- sharing

def resolve_sa_email():
    """Read the service account's client_email from GOOGLE_SVC_ACCT_PK_PATH."""
    sa_path = os.environ.get("GOOGLE_SVC_ACCT_PK_PATH")
    if not sa_path:
        die("GOOGLE_SVC_ACCT_PK_PATH is not set — cannot find the service "
            "account to share with.")
    if not os.path.exists(sa_path):
        die("GOOGLE_SVC_ACCT_PK_PATH points to a missing file: %s" % sa_path)
    try:
        with open(sa_path, "r", encoding="utf-8") as f:
            email = json.load(f).get("client_email")
    except Exception as e:
        die("Could not read service account JSON at %s: %s" % (sa_path, e))
    if not email:
        die("No client_email in service account JSON at %s." % sa_path)
    return email


def share_with_sa(token, file_id):
    email = resolve_sa_email()
    body = json.dumps({"type": "user", "role": "writer", "emailAddress": email}).encode()
    url = ("%s/%s/permissions?sendNotificationEmail=false&supportsAllDrives=true"
           % (DRIVE_FILES, file_id))
    http_json("POST", url, token=token, headers={
        "Content-Type": "application/json"}, data=body)
    return email


# ------------------------------------------------------------------ create

def create_native(args, mime, kind):
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
           "webViewLink": resp.get("webViewLink"),
           "sharedWith": share_with_sa(token, resp["id"])}
    print(json.dumps(out))


def cmd_create_doc(args):
    create_native(args, DOC_MIME, "doc")


def cmd_create_sheet(args):
    create_native(args, SHEET_MIME, "sheet")


# ------------------------------------------------------------------ upload

def cmd_upload(args):
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
           "webViewLink": resp.get("webViewLink"),
           "sharedWith": share_with_sa(token, resp["id"])}
    print(json.dumps(out))


# -------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="Create/upload to Google Drive as a real user.")
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
