---
name: codebase-rules
description: Codifies a project's de-facto architecture as one-decision-per-file ADRs in docs/adr/, the thing refactor-ticket cites. Surveys the code, grills each decision, writes the files. Re-run reconciles the record against the code and hands drift to challenge-adr.
disable-model-invocation: true
---

# codebase-rules

You turn a project's de-facto architecture and conventions into **recorded decisions**, one per `ADR-NNNN` in `docs/adr/`. An ADR is the single place a reviewer points to, as in "this violates ADR-0012", and the boundary an implementer is free to move within. Implementers get freedom on *how* code is written; what shape it must take is explicit and on record.

Every ADR follows [`ADR-FORMAT.md`](ADR-FORMAT.md). Read it before writing any file. One decision per ADR, no exceptions.

**A convention earns an ADR only if it binds.** Three tests, all required:

1. **Imperative.** It can be phrased as MUST or MUST NOT, not "we prefer" or "usually".
2. **Arguable.** You can name what it was chosen *against*. A decision with no losing alternative is not a decision, it's a description, and its Reason field will read as filler.
3. **Load-bearing.** A real reader would otherwise get it wrong. Skip anything that restates the language default or the obvious.

---

## Branch: setup or maintenance

Check `docs/adr/` for existing ADRs.

- **None found → setup.** Build the initial set from scratch.
- **Some found → maintenance.** Reconcile what's recorded against the current code.

---

## Survey (both branches, runs first)

Ground the decisions in what the code actually does. You are extracting decisions that already half-exist, not inventing a style guide. Read, don't ask, for anything the code can answer:

- Existing `docs/adr/`, `CONTEXT.md`, top-level `README.md`, and the directory tree.
- Sample across the codebase for the **de-facto conventions** a change will be judged against: layering and dependency direction, module and file placement, public-versus-private surface, naming, error handling and logging, test structure, config and dependency-injection boundaries. Note where the code is *consistent*, which is a candidate, versus where it *contradicts itself*, which needs a decision rather than an assumption.

Emit a short **"What I found"**: the conventions consistent enough to codify, and the inconsistencies that need resolving. Wait for the user to correct misreads before grilling.

---

## Setup

Work the candidates with the user under the `grilling` skill's mechanics, so invoke it. One question at a time, your recommendation first, explore before asking, walk each branch to resolution. This skill supplies *what* to resolve; `grilling` supplies *how*.

For each candidate:

1. **State the decision and your recommendation.** Draw the imperative from what the code already does where it's consistent. For an inconsistency, propose the shape you'd standardise on. The recommendation is input, not the verdict.
2. **Pin the Reason with the user, including what it beats.** This is the test of whether it's a real decision. If neither of you can name the alternative it was chosen over, it isn't one yet: drop it or sharpen it until you can.
3. **Pin the Consequence.** What this forces on future changes, and what breaks if someone routes around it. This is what a reviewer reads to tell compliance from breach, so it has to be concrete.
4. **Split anything with an "and"** into separate ADRs.
5. **Write the file** to `docs/adr/NNNN-slug.md` immediately on agreement, following `ADR-FORMAT.md` and taking the next free number. Capture each as it resolves; don't batch.

**Completion:** every consistent convention from the Survey is either written as an ADR or explicitly dropped with the user, and every inconsistency the Survey flagged is resolved into a decision or deferred by the user. List the ADRs created as clickable links.

---

## Maintenance

ADRs already exist. Your job here is **detection, not amendment.** Reconcile the recorded decisions against the code the Survey just read, and route each discrepancy:

- **Drift.** The code no longer matches a recorded decision. Report the breach. Either the code is wrong, which is work for the user or `refactor-ticket`, or the decision has been outgrown, which is a challenge. Say which you think it is.
- **New pattern.** A convention has emerged that no ADR covers. Run it through the setup flow above and write a new ADR.
- **Dead decision.** The code an ADR governed no longer exists.

**You do not edit or delete an existing ADR.** Not to fix drift, not to retire a dead decision, not to reword one. Every case is handed to the user to run as its own `/challenge-adr` session, named with the ADR and the discrepancy. That is the only door into a file that already exists, and this skill never opens it itself.

**Completion:** every existing ADR is confirmed still-accurate or handed back to the user with a named discrepancy and a pointer to `/challenge-adr`, and every new pattern the Survey found is either a new ADR or dropped. List what happened, one line each: created, drifted, or challenged.
