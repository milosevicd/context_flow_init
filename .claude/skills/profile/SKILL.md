---
name: profile
description: Use when the user wants to create a new profile or update an existing one by naming it and talking it through — the personal-context files in the profiles directory (e.g. CONSULTING, the "About me" context injected at session start). Trigger on phrases like "create a profile", "make a new profile", "new <name> profile", "update my profile", "add this to my <name> profile", "edit the consulting profile", "change my profile". A profile is a short first-person context document about the user in a given context (a role, a venture, a domain). Do NOT use this for project canon (that is canonize) or for Your own observations about the user (that is flag-a-pattern) — profiles are the user's own standing self-description, stored globally and reused across projects.
---

# Profile

Create and maintain **profiles** — short, first-person context documents about the
user in a particular context (a role, a venture, a domain). They live *outside* any
single project, in the shared profiles directory, and are reused everywhere. The
`CONSULTING` profile is the seed example: a few sentences establishing who the user
is and what they're doing, injected into context at session start under an
`# About me` heading.

A profile is **the user's own standing self-description** — what they'd want any
Claude session to know about them in that context. It is not project canon and not
your observations about them.

## Where profiles live

The profiles directory is resolved the same way the SessionStart hook resolves it:

```bash
DIR="${CLAUDE_PROFILES_DIR:-$HOME/.claude/profiles}"
```

- Read `$CLAUDE_PROFILES_DIR` if set; otherwise default to `~/.claude/profiles/`.
- One profile per file. **Filenames are UPPERCASE** with the `.md` extension —
  `CONSULTING.md`, `FITNESS.md`, `OPEN SOURCE.md` — matching the existing convention.
- The **name the user gives you is the filename** (uppercased). "my fitness profile"
  → `FITNESS.md`. If they give a multi-word name, keep the spaces and uppercase it.

## Profile format

Plain first-person prose. **No YAML frontmatter** — profiles are injected as raw
context, not parsed as memory files. Keep them tight:

- First person ("I am…", "I'm working on…"), present tense.
- A few sentences to a few short paragraphs — standing context, not a life story.
- Durable facts only: who they are, what they're doing, constraints and goals that
  hold across sessions. Leave fast-moving detail to project workspace/canon.

## Creating a new profile

1. **Resolve the directory** and check whether a file with that name already exists.
   If it does, this is an *update*, not a create — switch to the update procedure and
   tell the user.
2. **Talk it through.** Ask what this profile is for and what it should establish.
   Draft the prose with the user; a profile is built *through* conversation, not
   dictated. Pull in anything they've already told you that fits.
3. **Confirm the name** (→ uppercase filename) and **write the file** to the profiles
   directory.
4. Tell the user the path, and note that a new profile is **not auto-loaded** unless
   the SessionStart hook references it — only `CONSULTING.md` is wired in by default
   (see `.claude/settings.json`). If they want this profile injected automatically,
   offer to add it to the hook.

## Updating an existing profile

1. **Resolve the directory and read the current file** so you're editing the real
   content, not a guess. If the named profile doesn't exist, list what *does* exist
   and offer to create it instead.
2. **Talk through the change** — what to add, revise, or remove. Profiles are short,
   so prefer a clean rewrite that keeps the prose coherent over bolting on
   disconnected sentences.
3. **Rewrite the file** in place, preserving the first-person voice and concision.
   Don't pad it; a profile that grows sprawling has stopped being a profile.

## When the name is ambiguous

If the user says "update my profile" without naming which, **list the existing
profiles** (the files in the directory) and ask which one — unless there's only one,
in which case use it.

## Boundaries

- **Profiles vs canon:** a profile is the user's standing self-description, global
  and project-independent. Project facts, decisions, and reported events go to
  `canon/` via **canonize**.
- **Profiles vs reflections:** a profile is what the user says about themselves. What
  *You* notice about them — patterns, blind spots — goes to `reflections/` via
  **flag-a-pattern**.
- **Never invent** profile content. If you don't have enough from the user to write a
  section, ask rather than fabricate.
