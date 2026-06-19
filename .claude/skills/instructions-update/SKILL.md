---
name: instructions-update
description: USE PROACTIVELY whenever the user corrects your output, your approach, or the way you went about a task — and the correction implies a rule that should hold for future turns, not just this one. Trigger IMMEDIATELY on phrases like "don't do it that way", "stop doing X", "no, not like that", "fix this and don't repeat it", "next time, don't…", "remember not to…", "make a rule so you don't…", "you keep doing X — stop", or any feedback whose intent is to change Claude's process so the same mistake doesn't recur. ALWAYS invoke this skill BEFORE responding further to such feedback. Better to invoke once too often than to let a correction evaporate. However, If the user's feedback is a one-off preference for the current task only (not a durable rule), do NOT use this skill — just apply it in the moment.
---

# Instructions-update ritual

The user has just corrected you in a way that should change your future
behavior. Your job is to distill that correction into a durable rule and
record it in the project's `CLAUDE.md` before doing anything else.

## Step 1 — Distill the correction
Write the rule in one short sentence, in the imperative ("Use X, not Y",
"Never do Z", "When the user says A, do B"). It must be specific enough that
a future Claude reading `CLAUDE.md` cold can apply it without seeing this
conversation.

Also identify two short supporting lines:
- **Why:** the reason the user gave, or the mistake that triggered it.
- **How to apply:** when/where the rule kicks in.

If the correction is genuinely ambiguous — e.g., you cannot tell whether it
applies project-wide or only to the current task — ask the user in one short
sentence before writing. Do not invent scope silently.

## Step 2 — Read `CLAUDE.md`
The target is the project `CLAUDE.md` at the repository root
(`d:\obs\storage_calc\CLAUDE.md`). Read it in full so you can:
- Check whether a similar rule is already recorded (avoid duplicates).
- Locate the `## Always-loaded context` section, which must remain at the
  end of the file so its `@`-imports keep working as a footer.

## Step 3 — Write or update the entry

All Additional Instructions are equally important — there is no order, no ranking, no
date stamps.

Decide which of these three cases applies:

1. **New rule, no overlap with existing entries** → add a new bullet to the
   `## Additional Instructions` section. Position within the list does not matter.
2. **Refines or sharpens an existing rule** (same intent, better wording or
   added nuance) → edit the existing bullet in place. Do not duplicate.
3. **Contradicts an existing rule** → do NOT silently overwrite. Flag the
   conflict to the user in one sentence and ask whether to replace the old
   entry, merge it with the new one, or keep both.

Use this template for Additional Instructions:

```markdown
- **[Rule in one imperative sentence].**
  Why: [reason or triggering mistake].
  How to apply: [when/where this kicks in].
```

Keep each entry to those three lines — rule, Why, How to apply. If a single
line is enough, that's fine; drop the Why/How lines only when they would
add nothing beyond the rule itself.

## Step 4 — Confirm briefly
State what you captured and where, in one short sentence:
> Recorded to `CLAUDE.md` → ## Additional Instructions (new entry).

Use "(new entry)", "(updated existing entry)", or "(flagged conflict)" as
appropriate. Do not echo the full file or the full section unless asked.

## Hard rules
- NEVER modify any file under `/raw_input/`.
- NEVER silently overwrite or delete an entry that contradicts the new
  rule. Surface the conflict and let the user decide.
- NEVER move or alter the `## Always-loaded context` section or its
  `@`-imports; the new section goes ABOVE it.
- If the correction is too vague to write a specific rule, ask one
  clarifying question rather than guessing.
- Write rule entries in **British English** (see CLAUDE.md). Portuguese
  terms with specific legal/contractual meaning may be kept in
  Portuguese, italicised, where they would otherwise lose meaning in
  translation.