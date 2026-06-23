---
name: gdrive-create
description: USE whenever the user wants to CREATE a new Google Doc or Google Sheet, or UPLOAD a local file into Google Drive. Trigger on phrases like "create a new doc/sheet in Drive", "make a Google Doc", "start a new spreadsheet", "put this file in Drive", "upload X to the folder", "add a document to <folder>". This skill creates files with a domain-wide-delegated service account that impersonates a real user (who has Drive quota), then hands them to the google-drive MCP for editing. Do NOT use for editing existing files (use the MCP tools for that).
---

# Create / upload in Google Drive (domain-wide delegation)

The `google-drive` MCP server can *edit* existing files but cannot *create*
them. This skill fills that gap with a self-contained Python helper
([scripts/gdrive.py](scripts/gdrive.py), stdlib only — no pip installs).

The helper authenticates with a **domain-wide-delegated (DWD) service
account** that **impersonates a real user** (`GOOGLE_USER_EMAIL`). Because
the file is created *as that user* — who has normal Drive storage quota —
creation succeeds and the file lands in that user's own Drive. The user
owns it, so no separate sharing step is required.

**Typical flow:** this skill creates the empty Doc/Sheet → then use the
existing `mcp__google-drive__*` tools to write content into it.

## Prerequisites (supplied by the user, not the skill)

The skill does **not** mint credentials and never runs a browser/auth
flow. It signs a short-lived JWT with the service account key and exchanges
it for an access token. Everything is provided through environment
variables:

- `GOOGLE_DWD_SVC_ACCT_PK_PATH` — path to the service-account JSON key. The
  service account must have **domain-wide delegation** enabled and be
  authorized for the Drive scope
  (`https://www.googleapis.com/auth/drive`).
- `GOOGLE_USER_EMAIL` — the user the service account impersonates. Files are
  created in this user's Drive.

If either is missing, the script prints a clear JSON error saying exactly
what to set. **Surface that message to the user and stop — do not attempt
to authenticate or work around it.**

## Commands

Always run from the project root. Every command prints one JSON object
(`{"ok": true, "id": ..., "webViewLink": ...}` on success).

**Folder ID is required** for every create/upload — it is the long token
in a Drive folder URL (`.../folders/<FOLDER_ID>`). Never invent one.
Before running any command, be **certain** which folder the file belongs
in — see "Choosing the target folder" below.

**Never create in the Drive root.** Do not pass `root` (the Drive API's
special My Drive alias) as the folder, and never fall back to it when you're
unsure where a file belongs. A real folder ID is always required. The script
rejects `root` outright; if you don't have a real folder, ask the user (see
"Choosing the target folder") rather than defaulting to the top level.

## Choosing the target folder

Do **not** guess the folder. Be sure before you create anything — putting a
file in the wrong place is annoying to undo. Decide as follows:

1. **Obvious from this session?** If the user has already been working in a
   specific folder this session (e.g. you created or edited a file there
   earlier, or the user named it), and it's genuinely clear the new file
   belongs in that same folder, just use that folder ID. No need to ask.

2. **Otherwise, ask the user which folder.** Do not assume. To make the
   choice easier, you may use the `google-drive` MCP to list/search folders
   and present them as options. Note that the MCP runs as its *own* separate
   service account (not domain-wide delegation), so it only sees folders that
   have been **shared with that service account** — not the impersonated
   user's whole Drive. That's expected; create into one of those shared
   folders. Suggest a likely candidate, but let the user confirm or override.

3. **Only have a folder URL/ID?** Use it as given — extract the
   `<FOLDER_ID>` from the URL.

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
- NEVER commit secrets — the service-account JSON key. If asked to
  save/commit, exclude it.
- NEVER attempt to mint or refresh credentials yourself, and never run a
  browser auth flow. The script signs the JWT and exchanges it for a token;
  that is the only credential step.
- This skill only **creates/uploads**. For editing existing files, use
  the `mcp__google-drive__*` tools — do not reimplement them here.
- Folder ID is mandatory; never fabricate one. Be sure of the target
  folder first (see "Choosing the target folder") — reuse the session's
  obvious folder, otherwise ask the user; never assume.
- NEVER use the Drive root (`root` alias) as the destination. The script
  refuses it; if no real folder is known, ask — don't default to the root.
- Pass through the script's JSON errors verbatim in plain language;
  don't retry blindly on an auth/quota error.
