---
name: flag-a-pattern
description: Use when you notice a durable pattern in the user that the user has NOT stated themselves — a blind spot, a recurring behavior or rationalization, or a tension between a stated goal and their actual behavior — and it should be recorded as a provisional observation in `reflections/`. Trigger when such a pattern recurs, or on a first notable sighting worth tracking tentatively; also use when revising, strengthening, weakening, or retiring an existing observation, including when the user pushes back on one. This is the capture ritual behind the always-on Challenge stance. Do NOT use it for things the user explicitly said or decided — that is canonize. Flag-a-pattern records what *You* noticed; canonize records what the *user* said.
---

# Flag a pattern

Record an observation about the user in `reflections/` — Your own provisional
model of their patterns and blind spots. This is the one tier where you hold a view
the user didn't dictate, so hold it honestly *and* loosely: these are hypotheses,
not facts, and they carry lower authority than canon.

## When to flag

Flag when you notice something the user **hasn't said about themselves**:

- a blind spot — something they consistently don't see
- a recurring behavior or rationalization
- a tension between a stated goal (often in `canon/`) and their actual behavior

The defining test: **you noticed it, they didn't state it.** If the user explicitly
said or decided the thing, that's `canonize`, not this.

**Threshold:** one instance is an anecdote, and a single instance **never** creates
an *active* pattern. A single notable instance may create a *tentative* pattern only
when one of these holds:

- it is unusually strong,
- it has significant impact on project outcomes,
- or it directly contradicts an established canon goal.

Absent one of those, wait for recurrence before recording anything at all. Promote a
tentative entry to active once the pattern recurs — don't wait for overwhelming
proof, but don't elevate a single data point to a confident or active claim either.

## Entry format

Each observation is a discrete, status-tracked entry:

```
### [Short claim, phrased as a pattern]
- Status: tentative | active
- Confidence: low | medium | high
- First noticed: YYYY-MM-DD · Last updated: YYYY-MM-DD
- Evidence: [[Decision Or Event]], [[Another Event]] — the behavioral trail, not verbatim quotes
- Tension with: [[Stated Goal]]   (only if it contradicts something in canon)
- Watch for / act on: what to do differently when this observation is live
```

`Status` is just lifecycle stage: **tentative** (a watch-item, seen once or twice,
not yet promoted) or **active** (a working belief you use as a lens). `Confidence`
is strength of belief.

The two axes are related at the edges, not fully independent: a **tentative** entry
should stay **low/medium** confidence (it's seen once or twice), and **high**
confidence is only earned through recurrence, which by then means the entry is
**active**. So `tentative + high` should essentially never occur — if you're
reaching for high confidence, the entry has recurred enough to promote. A fading
observation is one whose confidence is dropping back down.

All active and tentative entries live in a single file,
`reflections/patterns.md`. Retired entries get moved to `reflections/_archive.md` so
the main file stays lean. (Both are fixed system filenames — they don't follow the
Title-Case-topic-file convention.)

## The write procedure

1. **Add or revise the entry** in `reflections/patterns.md` using the format above.
   Link evidence to the `workspace/` decisions, `canon/` files, or `raw_input/`
   sources that ground it, with `[[filename]]` pointer links.
2. **Update the entry's `Last updated`** date (and `Status` / `Confidence` if the
   evidence moved them).

## Revising and retiring

Reflections are **revisable**, unlike append-only canon:

- Update status and confidence as evidence accumulates or fades.
- **Retire, don't delete.** When an observation no longer holds, move it to
  `reflections/_archive.md` with a date and a one-line reason ("retired
  YYYY-MM-DD — user has confronted this three times this quarter"). The record of
  how your model of the user changed is itself worth keeping.
- The user can veto any entry. If they say an observation is wrong, retire it —
  don't defend it.

## Guards against bias

- **Require recurrence** before raising confidence; keep single-sighting entries
  tentative.
- **Seek disconfirmation.** When you find evidence *for* an existing observation,
  also ask what would count against it. Entries must stay falsifiable, not become
  self-fulfilling. This matters doubly because `patterns.md` is loaded into context
  every session: an always-present observation is the easiest one to keep
  confirming. Before you let a loaded pattern shape your read of the moment, look
  for the evidence that would *weaken* it.
- **Phrase as patterns and hypotheses, never verdicts.** "Tends to withdraw when
  criticized," not "is defensive." The framing keeps the observation usable and fair.

## Relationship to the Challenge stance

Challenging the user's reasoning where it improves the outcome is a standing
behavior — it happens whether or not this skill fires, and it doesn't mean
manufacturing disagreement. This skill is only the *recording* half: when a live
challenge reveals a pattern worth keeping, capture it here.
