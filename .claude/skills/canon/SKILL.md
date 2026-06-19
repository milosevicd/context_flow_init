---
name: canon
description: USE PROACTIVELY whenever the user shares ephemeral information that has no source document — verbal/conversational input that needs to be captured before it's lost. Trigger IMMEDIATELY on phrases like "I just talked to…", "I had a thought about…", "from the call with…", "remember that…", "I noticed…", "I realized…", "they told me…", "quick note…", or any time the user reports a fact, observation, decision, or quote with no accompanying file. ALWAYS invoke this skill BEFORE responding to such input. Do not wait to be asked. Better to invoke once too often than to lose information.
---

# Canon ritual

The user has shared ephemeral verbal input. There is no source document.
Your job is to preserve both the user's exact words AND a clean structured
interpretation, in the right canon file, before doing anything else.

## Step 1 — Identify the topic
Decide which canon file this belongs to. Standard topics:
- `canon/users.md` — homeowners, target user understanding, interview insights
- `canon/market.md` — competitors, alternatives, positioning
- `canon/domain.md` — storage volumes, cabinet/cupboard conventions, renovation realities
- `canon/product.md` — feature decisions, UX, principles

If none of these fit, propose a new topic file (e.g., `canon/pricing.md`) and
confirm the name with the user in one short sentence before creating it.

## Step 2 — Read the existing canon file (if it exists)
Before writing, read the current state. You must understand:
- The existing `Canonical` section MUST NOT be rewritten — only appended to.
- The existing `Verbatim notes` section is strictly append-only.

If the file does not exist, you will create it using the template below.

## Step 3 — Append the verbatim entry
Append to the `Verbatim notes` section, using today's date:

```
> YYYY-MM-DD — [user's exact words, in their voice; lightly cleaned for typos
> and filler ("um", "like") but preserve phrasing, framing, and meaning]
```

Quote the user. **Do not paraphrase into your own voice in this section.** If
the input is long, keep it as one quoted block — do not split or summarize.

## Step 4 — Update the Canonical section
- **Existing topic**: append a small structured addition that integrates the
  new input with what's already there. Do NOT rewrite or restructure prior
  content. Use a clean, neutral voice — this is your interpretation, not a
  quote.
- **New topic**: write the initial canonical interpretation, structured with
  short headings or bullets as appropriate.

## Step 5 — Update `canon/_index.md`
If you created a new canon file, append a one-line entry:

```
- `canon/[topic].md` — [one-line summary of what this topic covers]
```

If updating an existing file, leave the index alone UNLESS its summary line no
longer reflects the file's scope (in which case rewrite that one line).

## Step 6 — Confirm briefly
State what you captured and where, in one short sentence:
> Captured to `canon/users.md` (verbatim + canonical update).

Do not echo the full file content unless asked.

## Hard rules
- NEVER edit any file under `/raw_input/`.
- NEVER rewrite or restructure prior content in the `Canonical` section.
- NEVER paraphrase the user's words inside `Verbatim notes`.
- ALWAYS use today's date for the verbatim stamp.
- If unsure which topic fits, ask in one sentence — do not invent silently.
- Write the `Canonical` section in **British English** (see CLAUDE.md). Portuguese terms with specific legal/contractual meaning (e.g., *empreitada*, *dono de obra*, *caderno de encargos*) may be kept in Portuguese, italicised, with a brief English gloss on first use. **Do not** apply British spelling to `Verbatim notes` — those preserve the user's exact words regardless of dialect.

## Canon file template (for new topics)

```markdown
# [Topic]

## Canonical
[Structured interpretation — clean, neutral voice. Append-only.]

## Verbatim notes
> YYYY-MM-DD — [user's exact words]
> YYYY-MM-DD — [user's exact words, note 2]
...
```
