---
name: talk-to-middleschooler
description: >
  Word an explanation for a curious middle schooler who knows nothing about the
  subject, with every naked term glossed before use. Use when the user asks for a
  simple or plain-English explanation, says they don't know the area, asks
  "explain it simply", or when another skill needs its output worded for a
  complete non-expert.
---

# talk-to-middleschooler

Assume the reader is a curious middle schooler who knows nothing about this subject. Not "a little". Nothing.

Sacrifice grammar so a middle schooler can understand.

This skill owns wording only. It does not change what work gets done, what is true, or how long the answer is.

## Glossing

Invoke the `gloss-me` skill to find and gloss every naked term, with its floor lowered to nothing. Only the user's glossary counts as known. A term defined in a project doc is still naked.

The word being central to the subject makes it more likely to be naked, not less. Central words are exactly the ones assumed and never explained.

Gloss in plain words, in `gloss-me`'s block before the paragraph that uses the term:

New terms
- **race**, two bits of code touching the same thing at the same time, where whoever gets there first wins.

## Rules

- Name a thing by what it does before saying what it is called.
- Keep the real term in parentheses so the user can search it later: "the waiting list jobs sit in (a queue)".
- One idea per sentence. Short sentences. Fragments fine.
- Concrete over abstract. Any invisible mechanism gets an everyday analogy.
- The point first, the detail after.
- Plain word beats precise word whenever both are true.
- No equations. Say the relationship in words.

## Stays exact

Code blocks, commands, file paths, error strings, and identifiers are copied verbatim, never simplified and never renamed. Explain around them in plain words.

## Examples

**"Why is this query slow?"**

> Bad: The N+1 pattern here means the ORM issues a query per row instead of eager-loading the relation.
>
> Good: The code asks the database one question, gets 500 rows, then asks the database 500 more questions, one per row. 501 trips instead of 2. Fetching everything up front in one go fixes it (called eager loading).

**"What does this middleware do?"**

> Bad: It validates the JWT and short-circuits unauthorised requests.
>
> Good: Every request to the site passes through this file first, like a bouncer at a door. It checks the visitor's pass, which is a signed token the login step handed out (a JWT). If the pass is fake or expired, it turns them away before they reach anything real.
