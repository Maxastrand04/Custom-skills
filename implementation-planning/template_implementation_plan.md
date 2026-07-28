# N.N — Plan Name

One sentence describing what this plan accomplishes.

**Goal:** What the completed plan should achieve — the concrete outcome or capability that will exist when all phases are done.

**Branch:** Branch the implementer works from. From-issue plans: `<issue-number>-<slug from the issue's `## Branch` section>`. Standalone plans: a new branch name, or an existing branch the user named.

**Status legend:**  ⬜ Not started · 🟡 In progress · ✅ Done

---

## Acceptance criteria

What "done" means, terse — sacrifice grammar for brevity. **This is the contract the final Verification phase tests against**, and the only place testing is verified end-to-end in this plan. If a criterion can't be verified mechanically, mark it `(manual)` — the Supervisor will ask the user to confirm.

- AC-1: outcome. Verify: `tests/path/test_file.py::test_name` (written in Phase 1, re-run in Verification).
- AC-2: outcome. Verify: `tests/path/test_file.py::test_name`.
- AC-3 (manual): outcome. Verify: what the user looks at to confirm — no automated test, skipped in Phase 1.

On from-issue plans, these are lifted from the issue body and assigned `AC-N` IDs. On standalone plans, they come out of the grill.

---

## Rules in play

The project's architecture and coding rules live as one-rule-per-ADR files in `docs/adr/` (authored by `codebase-rules`), **not** in this plan. This section only points at the rule-ADRs this change operates under, so the implementer loads the right boundaries and the reviewer knows where to look. The implementer keeps freedom on *how* the code is written within these rules; the code-review session enforces them against the committed diff.

One line per rule-ADR: link, then that ADR's `**Rule:**` line **verbatim** — the ADR is the single source of truth, so never paraphrase or trim it. Only files carrying a `**Rule:**` line belong here; classic decision-ADRs and any rule marked `Status: deprecated` do not.

- [ADR-0007 — Handlers depend inward](../docs/adr/0007-handlers-depend-inward.md) — Code in `handlers/` MUST NOT import from `infra/`; depend on `core/` interfaces instead.
- [ADR-0012 — No ORM in domain](../docs/adr/0012-no-orm-in-domain.md) — Domain models MUST NOT import the ORM; persistence lives in `repos/`.

If no rule-ADR applies directly, replace the list with a single line: _"No specific rule-ADR applies; the general rule set in `docs/adr/` governs at review."_ If the project has no `docs/adr/` at all, say so instead and note that `codebase-rules` hasn't been run. If planning surfaced a project-wide structural choice no rule covers, that was turned into a new rule-ADR via `codebase-rules` before this plan was written — reference it here, don't decide it inline.

---

## Phase 0 — Preflight

Preflight holds only genuine **blockers** that must clear before execution can start — an external credential, a created resource, a decision that can't be made until execution time. It is **not** an assumption-confirmation checklist. Rows needing a code fact may be handed to a `claude` subagent; a row flips ✅ when the blocker actually clears. If there are no blockers, keep the single `None` row so execution goes straight to Red.

| Task | File | Status |
|------|------|--------|
| None — no blockers | — | ✅ |

---

## Phase 1 — Red

**This phase is mandatory and always second.** Write the actual failing (red) automated tests named in every non-`(manual)` `AC-N`'s verify clause, using the project's existing test framework and conventions. No implementation code — a test in this phase must fail because the behavior doesn't exist yet, never because of a broken test. Implementation phases below make these tests pass; Verification re-runs them as proof.

### Group 1 — [short name]

One line describing which `AC-N` tests this group writes and why they bundle together (shared test file or single atomic change).

| Task | File | Status |
|------|------|--------|
| Write test for AC-1 | [test_file.py](../tests/path/test_file.py) | ⬜ |
| Write test for AC-2 | [test_file.py](../tests/path/test_file.py) | ⬜ |

---

## Phase 2 — Green: [Phase Name]

Brief description of what this phase delivers. A Green phase makes the Red tests pass.

### Group 1 — [short name]

One line describing what this group changes and why these tasks bundle together (shared file or single atomic change).

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |
| Description of task | [filename](../path/to/file.py) | ⬜ |

### Group 2 — [short name]

One line describing this group.

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

---

## Phase 3 — Green: [Phase Name]

Brief description of what this phase delivers.

### Group 1 — [short name]

One line describing this group.

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

---

## Phase N — Verification

**This phase is mandatory and always last. No new code is written here — it checks one thing: that the code works, every `AC-N` test green.** It does **not** sweep architecture; a separate code-review session judges the committed diff against the rule-ADRs in `docs/adr/` (see `## Rules in play`). No other phase or Group carries a test block. On any failure, the Supervisor stops immediately and escalates to the user — no automatic retry, no fixed attempt cap; the user decides what happens next each time.

### Group 1 — Acceptance criteria

| Task | File | Status |
|------|------|--------|
| Verify AC-1 | — | ⬜ |
| Verify AC-2 | — | ⬜ |
| Verify AC-3 (manual) | — | ⬜ |

**Checks:** one row per `AC-N` from `## Acceptance criteria` — re-run the exact test named in its `Verify:` line (written in Phase 1) and confirm it now passes green; `(manual)` rows are confirmed with the user instead. Auto-rendered from the AC section by the planner — do not edit independently.

---

## Claude Instructions

Context and constraints that help Claude implement this plan correctly:

- **Rules binding:** Stay within the rule-ADRs in `docs/adr/` (those in `## Rules in play` apply directly). You have freedom on *how* to implement within them — no per-Group architecture approval is required. If the change forces a structural choice no rule covers and it's project-wide, stop and flag it for a `codebase-rules` ADR rather than improvising a one-off. The code-review session enforces the rule-ADRs on the commit.
- **Conventions:** Naming, file structure, patterns to follow from the existing codebase (beyond what's already pinned in the rule-ADRs).
- **Constraints:** What NOT to do — things to avoid or stay in scope of.
- **Order dependency:** Any phases or tasks that must complete before others can start.
- **Testing:** `## Phase 1 — Red` writes the tests red; nothing is *verified* (i.e., no test is run and judged) until `## Phase N — Verification`, which re-runs those same tests and expects green. No Group or Phase before Verification carries a test/check block. Any Verification failure stops the plan immediately and goes to the user — there is no automatic retry.
</content>
