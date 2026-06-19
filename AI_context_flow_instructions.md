# Claude router

This is a **thinking space, not a build space** — research, synthesis,
decisions, drafts, and communications. There is no application code here.

## Path rules

- `raw_input/` — **read-only**. Never modify, rename, or delete. Quote and cite only.
- `canon/` — **append-only**, follow the canon template (below). Never rewrite the Verbatim notes section. The Canonical section may be extended but not overwritten.
- `workspace/` — **free edit**. Drafts, brainstorming, planning. Anything goes.

## Canon file template

Every file under `canon/` (including `canon/project.md` and anything in `canon/topics/`) follows this shape:

```
# [Topic]

## Canonical
[Claude's structured interpretation, built up over time]

## Verbatim notes
> YYYY-MM-DD — [verbatim what the user said, in their words]
> YYYY-MM-DD — [later addition]
```

The Verbatim notes section is strictly append-only with date stamps. The Canonical section can be appended to as new verbatim notes accumulate, but earlier canonical content is not rewritten.

## Additional Instructions

- **At the start of any topic, proactively explore the folder tree (at least 1–2 levels deep) and read the files whose titles match the topic — don't wait to be told which file to read.** The relevant directories are `canon/`, `workspace/` and `raw_input/`.
  Why: only few files are auto-loaded; so answering without first checking what already exists risks duplicating or contradicting captured context.
  How to apply: when a conversation turns to a topic, glob/list the tree to see what exists, infer relevance from folder and file names (e.g. talk of the CEO → `canon/topics/ceo_goals.md`; the survey → `workspace/survey/`, `raw_input/survey/`; stakeholders → `canon/topics/stakeholders.md`), and read those files before giving substantive advice. Always cite/quote `raw_input/` rather than modifying it.

- **When reading a `canon/` file for context, read only the `## Canonical` section — stop before `## Verbatim notes`.** The Canonical section already holds everything you need to reason and advise.
  Why: the Verbatim notes are an append-only audit log of what the user said, raw material that has already been distilled into the Canonical section. Re-reading it for context wastes tokens without adding anything you don't already have.
  How to apply: when reading a canon file purely to inform an answer, read up to the `## Verbatim notes` heading and stop (e.g. use a line limit or read only the leading portion). The one exception is when you are about to **append to or modify the Verbatim notes** (typically via the canon Skill) — then read the existing notes so your addition is correctly dated, formatted, and non-duplicative.

- **Proactively write and edit files in `/workspace/` whenever a discussion produces a conclusion, decision, or non-trivial framing — don't wait to be asked.**
  Why: this is a thinking space; conclusions reached in chat evaporate unless captured in the workspace.
  How to apply: during or right after any discussion that yields a decision, tradeoff resolution, new framing, or option set, create or update the appropriate file in `/workspace/` (decision logs, drafts, working notes) without prompting. Use `/canon/` only via the canon Skill for ephemeral verbal input with no source document.

- **Never end a response by asking follow-up questions or offering additional work.** State the response and stop — no "want me to…", "should I also…", "let me know if…", or similar trailing offers.
  Why: the user finds these trailing offers noisy and unwanted.
  How to apply: end every reply at the substantive answer; if a next step is genuinely needed, take it or wait for the user to direct it, rather than soliciting it.

- **When a contradiction or unresolved ambiguity in the user's stated facts would force you to guess at the meaning, stop and ask one direct clarifying question before building substantive advice on top of it.** This is the one exception to the "no trailing questions" rule above: clarifying questions go *before* the answer, not after, and only when guessing wrong would meaningfully change the advice.
  Why: flagged a contradiction in canon ("one-hour trial mentoring session" vs the 30-min CEO call already on the calendar) and then proceeded to give a long, confident answer built on a guess about which reading was correct — the guess was wrong and the entire answer had to be retracted.
  How to apply: if you have already written the ambiguity down (in canon, in a workspace doc, or in the live conversation), treat that as a stop signal, not a footnote. One short clarifying question beats a long answer that gets rolled back. Does not apply to minor ambiguities where either reading produces broadly the same advice.

@./canon/_index.md
@./canon/reflections/blind_spots.md