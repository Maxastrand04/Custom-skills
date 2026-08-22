---
name: talk-to-middleschooler
description: >
  Word an explanation for a curious middle schooler who knows nothing about the
  subject — no term used before it is glossed. Use when the user asks for a
  simple or plain-English explanation, says they don't know the area, asks
  "explain it simply", or when another skill needs its output worded for a
  complete non-expert.
---

# talk-to-middleschooler

Assume the reader is a curious middle schooler who knows nothing about this subject. Not "a little" — nothing.

Sacrifice grammar so a middle schooler can understand.

This skill owns wording only. It does not change what work gets done, what is true, or how long the answer is.

## Naked terms

A **naked term** is a domain word used before its gloss. Never ship one.

Gloss on first use: the word, then a plain-word definition in the same sentence, then use it freely afterwards.

> A **race** — two bits of code touching the same thing at the same time, and whoever gets there first wins — is what breaks this.

A term counts as already known only if it is defined in a `CONTEXT.md`, an ADR, or another doc already read in this conversation. Everything else is naked. The word being central to the subject makes it more likely to need a gloss, not less — central words are exactly the ones assumed and never explained.

Acronyms expand on first use, every session.

Never gloss a naked term with more naked terms. If the definition needs two new words, the explanation is too high up — go one level down and describe what the thing *does*.

## Rules

- Name a thing by what it does before saying what it is called.
- Keep the real term in parentheses so the user can search it later: "the waiting list jobs sit in (a queue)".
- One idea per sentence. Short sentences. Fragments fine.
- Concrete over abstract. Any invisible mechanism gets an everyday analogy.
- The point first, the detail after.
- Plain word beats precise word whenever both are true.
- No equations. Say the relationship in words.

## Stays exact

Code blocks, commands, file paths, error strings, and identifiers are copied verbatim — never simplified, never renamed. Explain around them in plain words.

## Examples

**"Why is this query slow?"**

> Bad: The N+1 pattern here means the ORM issues a query per row instead of eager-loading the relation.
>
> Good: The code asks the database one question, gets 500 rows, then asks the database 500 more questions — one per row. 501 trips instead of 2. Fetching everything up front in one go fixes it (called eager loading).

**"What does this middleware do?"**

> Bad: It validates the JWT and short-circuits unauthorised requests.
>
> Good: Every request to the site passes through this file first, like a bouncer at a door. It checks the visitor's pass — a signed token the login step handed out (a JWT) — and turns them away before they reach anything real if the pass is fake or expired.
