---
name: canonize
description: Use whenever the user states, decides, or reports something durable about the project that belongs in the permanent record — a fact, a decision, an intent, a lasting framing, OR a loose, informal account of something that happened (e.g. "I talked to the CEO and here's what came out of it", "the client pushed back on the timeline", a status update or recap). Trigger on cues like "remember this", "capture this", "for the record", "from now on", "let's decide", and also on plain situational reporting where the user is conveying durable information in loose form, even if they do not ask you to save it. This skill governs how to write the `canon/` files, whose Verbatim notes are append-only and whose Canonical synthesis is rewritten to stay current. Do NOT use it for Your own observations about the user's patterns or blind spots — that is the flag-a-pattern skill. Canonize records what the *user* said, decided, or reported; flag-a-pattern records what *You* noticed.
---

# Canonize

Commit durable, user-supplied input to `canon/` — the project's authoritative
record, produced *through* conversation with the user. This is a deliberate act:
canon is what later reasoning trusts without re-checking. The Verbatim notes are the
immutable log of what the user said; the Canonical section is your current synthesis
of those notes, which you keep rewritten to stay accurate.

(Contrast with `raw_input/`: that tier holds material the user filed directly with
no conversation around it. Canon is what gets distilled here when the two of you
actually talk something through.)

## When to canonize

Canonize when the user expresses something meant to outlive the conversation:

- a decision or commitment ("we're going with X", "from now on, Y")
- a durable fact about the project, its people, goals, or constraints
- a lasting framing or principle
- **a loose account of something that happened** — a conversation, a meeting, an
  event, a status update ("I talked to the CEO and here's what came out of it", "the
  client pushed back on the timeline"). The user is handing you durable information
  in informal form; distil it into the right topic file.
- anything they ask you to "remember" or put "on the record"

The defining test: **it came from the user** — what they said, decided, or reported.
If instead you are recording something *you* noticed that the user didn't state — a
pattern, a blind spot, a goal-vs-behavior tension — that is `flag-a-pattern`, not
this.

Don't canonize fast-moving scratch, half-formed ideas, or your own brainstorming
with the user — that belongs in `workspace/`. Canon is for what has settled or
actually happened: a reported event is durable (it occurred), even when described
loosely.

**A note on decisions (the canon / workspace boundary).** While a decision is still
*in flight* — options being weighed, reasoning still moving — it lives in a
`workspace/` decision log. Canonize the decision once it has actually *settled*:
the landing goes in canon, and the workspace log can stay as the trail that led
there. If you're unsure whether it's settled, it probably isn't yet — leave it in
workspace.

## Where it goes

One topic per file.

- The **project-level spine** lives in **`PROJECT.md`** at the project root (the
  all-caps system file, transcluded into context on every session). It carries the
  durable shape of the project as a whole.
- **Individual themes** live in `canon/<subfolder>/<Topic Name>.md` — directories
  lowercase, the topic file itself in Title Case With Spaces, e.g.
  `canon/topics/CEO Goals.md`, `canon/people/Mariana Suleman - Event Producer.md`.

If no file fits the topic yet, create one; if one exists, write into it.

## The canon file template

Frontmatter, then two sections:

```
---
summary: One to three sentences — what this file covers and when to read it.
status: active
updated: YYYY-MM-DD
---

## Canonical
### Facts
[Durable facts about the project, its people, goals, or constraints.]

### Decisions
[Settled decisions and commitments, and lasting framings or principles.]

### Reported Events
[Things that happened — conversations, meetings, status updates — in chronological order.]

## Verbatim notes
> YYYY-MM-DD — [the user's own words, quoted faithfully]
> YYYY-MM-DD — [later addition]
```

**Why three buckets — they age differently.** A reported event (`We spoke to the
CEO yesterday`) is a permanent historical fact: it happened, so events *accrue* and
are never overwritten, only added to and reinterpreted. A decision
(`We're targeting agencies`) is a reversible commitment a later note can supersede.
A fact (`The CEO holds 40% equity`) is corrigible — a later note can correct or
refine it. Sorting the synthesis this way keeps the reversible material visibly
separate from the permanent record.

Include only the subsections that have content; omit an empty heading rather than
leaving a placeholder. The same Verbatim notes log feeds all three subsections —
the split is in the Canonical synthesis, not in the notes.

## The write procedure

1. **Read the existing Verbatim notes first.** This is the one time you read past
   `## Canonical` for context — you need the full set of notes both to place your
   new one correctly and to rebuild the Canonical synthesis from all of them.
2. **Append a dated Verbatim note** capturing what the user said in *their* framing,
   prefixed `> YYYY-MM-DD — `. Quote short statements exactly; for a long loose
   report, capture their account faithfully and condense if needed, but never
   reinterpret it. The Verbatim section is strictly append-only: never edit,
   reorder, or rewrite an earlier note.
3. **Rewrite the Canonical section** as a clean synthesis of *all* the Verbatim
   notes, including the one you just added, sorted into **Facts**, **Decisions**,
   and **Reported Events** (omit any subsection with no content). Canonical is not
   append-only — it's the current best understanding, so update it freely. The
   subsections behave differently on conflict: in **Facts** and **Decisions**, where
   two notes genuinely conflict on the same point the **later note wins** — but don't
   let a tentative aside silently override a firm, explicit decision. **Reported
   Events** don't conflict this way — both events happened, so they accrue
   chronologically rather than overwrite each other; a later note can add context to
   an earlier event but never erases that it occurred. If a new note contradicts a
   settled prior fact or decision in a way that actually matters, surface it to the
   user rather than quietly overwriting.
4. **Link claims to their evidence** — the `raw_input/` source, the `workspace/`
   decision, or a related `canon/` file — using `[[filename]]` pointer links.
5. **Update the frontmatter**: refresh `summary` if the file's scope changed, and
   set `updated` to today.

## File lifecycle: superseding

A canon file rarely dies — Verbatim is append-only and Canonical just keeps getting
rewritten. But a *whole file* becomes **`status: superseded`** when its topic is
wholly replaced or migrated — e.g. the topic was reorganized into a different file,
or a decision was fully reversed and re-canonized elsewhere. When that happens:

- Set the file's frontmatter `status: superseded`.
- Add a line at the top of `## Canonical` linking the **successor** file
  (`Superseded by [[Successor File Name]] on YYYY-MM-DD — reason`).
- **Never delete it.** The append-only history stays; superseded files are skipped
  during normal orientation but remain for auditing.

## Invariants

- Verbatim notes are **never** rewritten — only appended, always dated. This is the
  immutable record, and it's what makes rewriting Canonical safe.
- Canonical is **a living synthesis** — rewrite it freely to stay current. On a
  genuine conflict within **Facts** or **Decisions** (one that counts as an update),
  later notes take precedence over earlier ones; **Reported Events** accrue instead
  of overwriting, since each event genuinely happened.
- Only the user's stated, decided, or reported input belongs here. Your own
  inferences go to `reflections/` via flag-a-pattern.
