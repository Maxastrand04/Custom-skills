---
name: talk-to-highschooler
description: >
  Word an explanation for a sharp high schooler — algebra and basic programming
  assumed, everything domain-specific glossed on first use. Use when the user
  wants an explanation pitched above beginner but without expert jargon, says
  the plain-English version is too dumbed down, or when another skill needs its
  output worded for a capable learner who is new to this particular domain.
---

# talk-to-highschooler

Assume the reader is a sharp high schooler: comfortable with algebra, functions, graphs, variables, loops, and what a function call is. New to *this* subject and its vocabulary.

Sacrifice grammar so a high schooler can understand.

This skill owns wording only. It does not change what work gets done, what is true, or how long the answer is.

## The floor

Assumed known, use freely: arithmetic and algebra, percentages, ratios, powers, basic probability, reading a graph; variables, functions, loops, conditionals, lists, files, running a command.

Not assumed, gloss on first use: everything domain-specific — the field's named concepts, its acronyms, its tools, its notation.

## Naked terms

A **naked term** is a domain word used before its gloss. Fine to use *once glossed* — that is the point of this level. Gloss it, then lean on it.

Gloss on first use: the word, then a one-clause definition, then use it as normal vocabulary for the rest of the conversation. Do not re-explain a term already glossed.

A term counts as already known only if it sits on the floor above, or is defined in a `CONTEXT.md`, an ADR, or another doc already read in this conversation.

Acronyms expand on first use, every session.

A gloss may lean on the floor, and on terms already glossed. It may not introduce a second new term.

## Rules

- Precision is kept. Say the real thing and define it; do not swap it for a vaguer word.
- Equations, notation, and pseudocode are welcome — name every symbol the first time it appears.
- Analogy is for genuinely counter-intuitive mechanics, not for everything.
- The point first, then the mechanism, then the caveat.
- Short sentences. One idea each. Fragments fine.

## Stays exact

Code blocks, commands, file paths, error strings, and identifiers are copied verbatim. Explain around them.

## Examples

**"Why is this query slow?"**

> Bad: The N+1 pattern here means the ORM issues a query per row instead of eager-loading the relation.
>
> Good: One query fetches 500 rows, then the loop fires one more query per row — 501 round trips instead of 2, so cost grows as N+1 rather than staying flat. The fix is to fetch the related rows up front in a single join (eager loading) instead of lazily, one at a time.

**"What does this middleware do?"**

> Bad: It validates the JWT and short-circuits unauthorised requests.
>
> Good: It runs before every route handler. It reads the request's token — a JWT, which is just JSON that the server signed so it can detect tampering — checks the signature and the expiry timestamp, and returns 401 immediately if either fails, so nothing downstream ever sees an unauthenticated request.
