---
name: commit-push
description: USE PROACTIVELY whenever the user asks to save the current work to the cloud / GitHub in one go. Trigger IMMEDIATELY on phrases like "commit the work", "commit all this", "commit the changes", "commit to GitHub", "commit to the cloud", "commit and push", "save to GitHub", "save to the cloud", "save my work", "back this up", or any similar instruction that means "snapshot everything that changed and get it onto the remote". ALWAYS invoke this skill BEFORE responding so the save actually happens. Do NOT trigger for partial-staging requests (e.g. "commit only file X"), message-only requests with no upload, or pure inspection ("show me what changed").
---

# Save-to-cloud ritual

The user wants every pending change snapshotted and uploaded to GitHub
in one operation. The user has pre-authorised the whole flow by
invoking this skill — do not ask for confirmation again.

**User-facing language: NO git terminology, ever.** The user is not a
technical git user. In any text shown to the user — status updates,
confirmations, error messages, conflict explanations — never say:
*commit, push, pull, rebase, merge, branch, master, origin, remote,
upstream, fast-forward, SHA, HEAD, staged, unstaged, working tree,
index, conflict markers, --force*. Use plain words instead: "save",
"saved", "upload", "the cloud copy", "the saved version", "your
changes", "the latest version on GitHub", "overlapping edits". The
underlying tool calls still use git of course; only the text the user
reads must be plain.

## Step 1 — Survey the changes
Run in parallel:
- `git status` (no `-uall` flag)
- `git diff` (working tree)
- `git diff --staged`
- `git log -n 5 --oneline` (to match the repo's message style)

If there are no pending changes, stop. Tell the user in one plain
sentence — e.g. "Nothing new to save." Do not create an empty entry.

## Step 2 — Draft the save message
- Read the actual diff. Summarise the *substantive* change, not the
  file list.
- One short subject line (≤ 72 chars), present tense, no trailing full
  stop. Match the style of recent entries in `git log`.
- Never add a body — subject alone is enough.
- **British English** throughout (see CLAUDE.md): "-ise/-isation",
  "behaviour", "organisation", etc.
- Do NOT add a `Co-Authored-By` trailer or any "Generated with Claude"
  footer.

## Step 3 — Stage and snapshot
- Stage by explicit paths (the ones surfaced by `git status`). Do NOT
  use `git add -A` or `git add .` — they sweep in untracked junk and
  potentially secrets.
- Skip anything that looks like a secret (`.env`, `*credentials*`,
  `*.key`, `*.pem`, tokens). If such a file is in the change set,
  pause and flag it to the user in one plain sentence — e.g. "There's
  a file that looks like it contains a password (`.env`) — should I
  leave it out?" — before continuing.
- Snapshot with the drafted message via a HEREDOC so multi-line
  formatting survives:
  ```
  git commit -m "$(cat <<'EOF'
  <subject>

  EOF
  )"
  ```
- NEVER pass `--no-verify`, `--no-gpg-sign`, or `--amend`. If a
  pre-snapshot hook fails, fix the underlying issue and create a NEW
  snapshot; never bypass the hook.

## Step 4 — Sync with the cloud copy, then upload
This repo always works on `master` with a remote `master` available.
Do NOT check the branch, do NOT switch branches, do NOT check whether
a remote exists. Assume `master` and `origin/master`.

- Pull cloud changes and replay the new local snapshot on top, so the
  upload is always a clean fast-forward:
  ```
  git pull --rebase origin master
  ```
- If the replay reports overlapping edits, attempt to auto-resolve:
  inspect each affected file, understand both sides, and produce a
  merged result that preserves the intent of both changes. After
  resolving, `git add` the resolved files and run `git rebase --continue`.
  Repeat until the replay finishes.
- Only stop and ask the user when the overlap is genuinely ambiguous
  — e.g. two sides edit the same line with semantically incompatible
  intent, the correct resolution depends on context you don't have,
  or merging both would corrupt the file. In that case run
  `git rebase --abort` to leave things clean, then explain in one or
  two **plain** sentences (no git terminology) what the two
  overlapping edits are and ask how to proceed. For example: "Two
  versions of `prd.md` changed the same paragraph in different ways —
  one says X, the other says Y. Which should I keep?"
- Then upload:
  ```
  git push origin master
  ```
- NEVER create a new branch.
- NEVER create a merge entry (no plain `git merge`, no `git pull`
  without `--rebase`, no `--no-ff`).
- NEVER use `--force` or `--force-with-lease`. If the upload is
  rejected for any reason after a clean replay, stop and tell the
  user in plain language ("Couldn't upload — something on the cloud
  side rejected the save. Want me to retry?").

## Step 5 — Confirm
One short, plain-language sentence. No SHAs, no branch names, no
"committed" / "pushed". Examples:
> Saved "tighten cascade rules" to GitHub.
> Saved your changes to GitHub.

Do not echo the diff or message body unless asked.

## Hard rules
- NEVER show git terminology to the user (see the user-facing
  language note at the top).
- NEVER snapshot without uploading in this skill — the whole point is
  "one go". If the upload fails, surface the failure in plain
  language; don't silently leave an un-uploaded snapshot behind
  without telling the user.
- NEVER stage with `-A` / `.`; always list files explicitly.
- NEVER use `--no-verify`, `--amend`, or force-upload variants.
- NEVER create branches or merge entries; always replay onto the
  cloud copy and fast-forward.
- NEVER touch `git config`.
- NEVER include files matching common secret patterns without
  flagging in plain language.
- British English for the save message and all user-facing text.
