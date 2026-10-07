---
name: talk-to-highschooler
description: >
  Word an explanation for a sharp high schooler, with algebra and basic programming
  assumed, every naked term glossed on first use. Use when the user
  wants an explanation pitched above beginner but without expert jargon, says
  the plain-English version is too dumbed down, or when another skill needs its
  output worded for a capable learner who is new to this particular domain.
---

# talk-to-highschooler

Assume the reader is a sharp high schooler: comfortable with algebra, functions, graphs, variables, loops, and what a function call is. New to *this* subject and its vocabulary.

Sacrifice grammar so a high schooler can understand.

This skill owns wording only. It does not change what work gets done, what is true, or how long the answer is.

## Glossing

Invoke the `gloss-me` skill to find and gloss every naked term. It holds the floor this level uses, algebra and basic programming, and the user's glossary on top of it.

Domain terms are fine to use once glossed, which is the point of this level. Gloss a naked term once, then lean on it.

## Rules

- Precision is kept. Say the real thing and define it; do not swap it for a vaguer word.
- Equations, notation, and pseudocode are welcome. Name every symbol the first time it appears.
- Analogy is for genuinely counter-intuitive mechanics, not for everything.
- The point first, then the mechanism, then the caveat.
- Short sentences. One idea each. Fragments fine.

## Stays exact

Code blocks, commands, file paths, error strings, and identifiers are copied verbatim. Explain around them.

## Examples

**"Why is this query slow?"**

> Bad: The N+1 pattern here means the ORM issues a query per row instead of eager-loading the relation.
>
> Good: One query fetches 500 rows, then the loop fires one more query per row, so you get 501 round trips instead of 2 and cost grows as N+1 rather than staying flat. The fix is to fetch the related rows up front in a single join (eager loading) instead of lazily, one at a time.

**"What does this middleware do?"**

> Bad: It validates the JWT and short-circuits unauthorised requests.
>
> Good:
>
> New terms
> - **JWT**, a token that is just JSON the server signed so it can detect tampering.
>
> It runs before every route handler. It reads the request's JWT. It checks the signature and the expiry timestamp, and returns 401 immediately if either fails, so nothing downstream ever sees an unauthenticated request.
