---
name: codebase-rules
description: Codify a project's architecture and coding rules as enforceable one-rule-per-ADR files in
  docs/adr/, the pillar a reviewer cites and an implementer stays within. Surveys the codebase, grills
  you into each rule, and writes docs/adr/NNNN-slug.md with a Rule / Why / How-to-check shape. Use when
  the user wants to set up codebase rules, codify conventions or architecture as ADRs, generate rule
  ADRs, or (on re-run) reconcile the rules against the current code.
---

# codebase-rules

You turn a project's de-facto architecture and coding conventions into **rules**, one enforceable rule per `ADR-NNNN` in `docs/adr/`. A rule-ADR is the single place a reviewer points to, as in "this violates ADR-0012", and the boundary an implementer is free to move within. The whole point is to give implementers freedom on *how* code is written while keeping *what shape it must take* explicit and checkable.

Every rule-ADR is written using [`RULE-ADR-FORMAT.md`](RULE-ADR-FORMAT.md). Read it before writing any file. One rule per ADR, no exceptions.

**A rule earns an ADR only if it is enforceable.** Three tests, all required:
1. **Imperative.** It can be phrased as MUST or MUST NOT, not "we prefer" or "usually".
2. **Checkable.** A reviewer, or a grep, can look at a diff and say complied or violated. If you can't write the `How to check` line, it isn't a rule yet.
3. **Load-bearing.** A real reader would otherwise get it wrong. Skip rules that just restate the language default or the obvious.

A vague preference that fails these isn't a rule. Leave it out rather than writing a soft ADR nobody can cite.

---

## Branch: setup or maintenance

Check `docs/adr/` for existing rule-ADRs (files carrying a `**Rule:**` line).

- **None found → setup.** Build the initial rule set from scratch (below).
- **Some found → maintenance.** Reconcile the existing rules against the current code (below).

---

## Survey (both branches, runs first)

Ground the rules in what the code actually does. You are extracting rules that already half-exist, not inventing a style guide. Read, don't ask, for anything the code can answer:

- Existing `docs/adr/` (rule and classic ADRs both), `CONTEXT.md`, top-level `README.md`, and the directory tree.
- Sample across the codebase for the **de-facto conventions** the change will be judged against: layering and dependency direction, module/file placement, public-vs-private surface, naming, error-handling and logging patterns, test structure/conventions, config and dependency-injection boundaries. Note where the code is *consistent* (a candidate rule) versus where it *contradicts itself* (a rule to be decided, not assumed).

Emit a short **"What I found"** summary: the conventions that look consistent enough to codify, and the inconsistencies that need a decision. Wait for the user to correct misreads before grilling.

---

## Setup

Work through the candidate rules with the user under the `grilling` skill's mechanics, so invoke it. That means one question at a time, your recommendation first, explore before asking, and walk each branch to resolution. This skill supplies *what* to resolve; `grilling` supplies *how*.

For each candidate surfaced by the Survey:

1. **State the rule and your recommendation.** Draw the imperative from what the code already does where it's consistent. For an inconsistency, propose the shape you'd standardise on and why. The recommendation is input, not the decision.
2. **Pin the `How to check` line with the user.** This is the test of whether it's a real rule. If neither of you can say how a reviewer would catch a violation, drop it or sharpen it until you can.
3. **Split anything with an "and"** into separate rules, one rule per ADR.
4. **Write the rule-ADR** to `docs/adr/NNNN-slug.md` immediately on agreement, following `RULE-ADR-FORMAT.md` and taking the next free number. Capture each as it resolves, and don't batch. Skip the file for anything that fails the three enforceability tests.

**Completion:** every consistent convention from the Survey is either written as a rule-ADR or explicitly dropped (with the user) as not enforceable, and every inconsistency the Survey flagged has been resolved into a rule or deferred by the user. List the ADRs created as clickable links.

---

## Maintenance

Rule-ADRs already exist. Reconcile them against the code the Survey just read, and close the loop with the user on each discrepancy:

- **Drift.** The code no longer matches a rule. Decide with the user whether the rule is still right, in which case the code is wrong and you note it for the reviewer, or the rule has been outgrown, in which case you amend the ADR or set `Status: deprecated`.
- **New pattern.** A convention has emerged that no rule covers. Run it through the setup flow: state it, pin `How to check`, split it, then write a new ADR.
- **Dead rule.** A rule about code that no longer exists. Mark it `deprecated`, or `superseded by ADR-NNNN`, rather than deleting it, so review history still resolves the number.

Never silently rewrite a rule's meaning. A change to what an ADR requires goes through the user, because live review comments and plans cite these numbers.

**Completion:** every existing rule-ADR is confirmed still-accurate or explicitly amended/deprecated with the user, and every new pattern the Survey found is either a new rule-ADR or dropped. List what changed (created / amended / deprecated), one line each.
