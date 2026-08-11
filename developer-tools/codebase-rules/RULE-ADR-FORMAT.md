# Rule-ADR Format

Rule-ADRs live in `docs/adr/` alongside classic decision-ADRs and share the same sequential numbering: `0001-slug.md`, `0002-slug.md`, … Create `docs/adr/` lazily — only when the first ADR is written.

A rule-ADR differs from a classic decision-ADR in one way: it states an **enforceable rule** a reviewer can cite and check, not just a decision that was made. The `**Rule:**` line is what marks a file as a rule-ADR.

## Template

```md
# ADR-NNNN — {imperative rule title, e.g. "Handlers depend inward"}

**Rule:** {one imperative sentence — MUST / MUST NOT}. e.g. "Code in `handlers/` MUST NOT import from `infra/`; depend on `core/` interfaces instead."

**Why:** {1–2 sentences — the trade-off or principle this protects}.

**How to check:** {what a reviewer or a grep looks for to confirm compliance — concrete enough to verify against a diff}.
```

The filename slug is the rule's shorthand — pick it so `docs/adr/` reads as an index of rules at a glance (`0012-no-orm-in-domain.md`, not `0012-database.md`).

## Optional lines

Add only when they earn their place:

- **Scope:** paths/layers/contexts the rule applies to, when it isn't the whole repo.
- **Status:** `accepted | deprecated | superseded by ADR-NNNN` — set when a rule is retired or replaced rather than deleted.
- **Exceptions:** narrow, named carve-outs — but a rule riddled with exceptions is a sign it's really two rules or none.

## One rule per file

Never bundle two rules in one ADR. The whole value is that `ADR-0012` names exactly one thing, so a review comment ("violates ADR-0012") is unambiguous and the reader loads only that file. If a candidate rule has an "and" in it, split it.

## Numbering

Scan `docs/adr/` for the highest existing number (across both rule-ADRs and classic ADRs) and increment by one.
