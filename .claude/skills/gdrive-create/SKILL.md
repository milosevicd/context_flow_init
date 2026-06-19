---
name: gdrive-create
description: USE whenever the user wants to CREATE a new Google Doc or Google Sheet, or UPLOAD a local file into Google Drive. Trigger on phrases like "create a new doc/sheet in Drive", "make a Google Doc", "start a new spreadsheet", "put this file in Drive", "upload X to the folder", "add a document to <folder>". The google-drive MCP server uses a service account that has NO storage quota and therefore CANNOT create files — this skill creates them as a real user (OAuth) and hands them to the MCP for editing. Do NOT use for editing existing files (use the MCP tools for that).
---

# Create / upload in Google Drive (real-user OAuth)

The `google-drive` MCP server authenticates with a **service account**.
Service accounts have no personal Drive quota, so `files.create` fails
with `storageQuotaExceeded` in any My-Drive folder. The MCP can *edit*
files but cannot *create* them.

This skill fills that gap: a self-contained Python helper
([scripts/gdrive.py](scripts/gdrive.py), stdlib only — no pip installs)
that authenticates as a **real user** via an OAuth client id/secret plus
a refresh token, creates the file, and always shares it with the
service account so the MCP can immediately edit it.

**Typical flow:** this skill creates the empty Doc/Sheet → then use the
existing `mcp__google-drive__*` tools to write content into it.

## Prerequisites (supplied by the user, not the skill)

The skill does **not** mint credentials and never runs a browser/auth
flow. The user obtains a refresh token once, outside the skill, and
provides everything through environment variables:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REFRESH_TOKEN`
- `GOOGLE_SVC_ACCT_PK_PATH` — path to the service-account JSON (the same
  env var the MCP uses). Every new file is automatically shared with its
  `client_email` so the MCP can edit it.

If any of these is missing, the script prints a clear JSON error saying
exactly what to set. **Surface that message to the user and stop — do not
attempt to authenticate or work around it.**


## Commands

Always run from the project root. Every command prints one JSON object
(`{"ok": true, "id": ..., "webViewLink": ...}` on success).

**Folder ID is required** for every create/upload — it is the long token
in a Drive folder URL (`.../folders/<FOLDER_ID>`). Never invent one.
Before running any command, be **certain** which folder the file belongs
in — see "Choosing the target folder" below.

Every new file is automatically shared (writer access) with the project's
service account — read from `client_email` in the JSON at
`GOOGLE_SVC_ACCT_PK_PATH` — so the `google-drive` MCP can edit it straight
away. No flag is needed for this.

## Choosing the target folder

Do **not** guess the folder. Be sure before you create anything — putting a
file in the wrong place is annoying to undo. Decide as follows:

1. **Obvious from this session?** If the user has already been working in a
   specific folder this session (e.g. you created or edited a file there
   earlier, or the user named it), and it's genuinely clear the new file
   belongs in that same folder, just use that folder ID. No need to ask.

2. **Otherwise, ask the user which folder.** Do not assume. To make the
   choice easier, you may use the `google-drive` MCP to list/search the
   folders shared with the service account and present them as options
   (read the service account's `client_email` from the JSON at
   `GOOGLE_SVC_ACCT_PK_PATH` to know whose shares you're looking at).
   Suggest a likely candidate, but let the user confirm or override.

3. **The folder need not be shared with the service account.** The user may
   legitimately choose a folder the service account can't see — this file
   will be shared with the service account separately, on its own, after
   creation (the create command already grants the service account writer
   access to the *file*). So a folder missing from the shared list is not a
   blocker; the shared-folder list is only an aid to help the user choose.
   If you only have a folder URL/ID from the user, use it as given.

Once you have the right folder ID, run the appropriate command below.

### Create an empty Google Doc
```
python .claude/skills/gdrive-create/scripts/gdrive.py create-doc \
  --name "Proposal — Client X" --folder <FOLDER_ID>
```

### Create an empty Google Sheet
```
python .claude/skills/gdrive-create/scripts/gdrive.py create-sheet \
  --name "Pricing model — Client X" --folder <FOLDER_ID>
```

### Upload an existing local file (any format)
```
python .claude/skills/gdrive-create/scripts/gdrive.py upload \
  --file ./report.pdf --folder <FOLDER_ID>
```
Add `--convert doc` or `--convert sheet` to turn an uploaded
`.docx`/`.xlsx`/`.csv`/etc. into a native Google Doc/Sheet. Omit it to
store the file in its original format. Add `--name` to rename on upload.

## After creating

Report back the `webViewLink` to the user. To populate content, switch to
the MCP tools (`mcp__google-drive__insertText`,
`mcp__google-drive__writeSpreadsheet`, `mcp__google-drive__batchWrite`,
etc.) using the returned `id`.

## Hard rules
- NEVER commit secrets — the refresh token, client secret, or the
  service-account JSON. If asked to save/commit, exclude these.
- NEVER attempt to mint or refresh credentials yourself. If the refresh
  token is missing, relay the script's message and stop.
- This skill only **creates/uploads**. For editing existing files, use
  the `mcp__google-drive__*` tools — do not reimplement them here.
- Folder ID is mandatory; never fabricate one. Be sure of the target
  folder first (see "Choosing the target folder") — reuse the session's
  obvious folder, otherwise ask the user; never assume.
- Pass through the script's JSON errors verbatim in plain language;
  don't retry blindly on an auth/quota error.
