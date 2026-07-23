# N.N — Plan Name

One sentence describing what this plan accomplishes.

**Goal:** What the completed plan should achieve — the concrete outcome or capability that will exist when all phases are done.

**Branch:** Branch the implementer works from (new branch name, or an existing branch the user named).

**Status legend:**  ⬜ Not started · 🟡 In progress · ✅ Done

---

## Acceptance criteria

What "done" means, terse — sacrifice grammar for brevity. **This is the contract the final Verification phase tests against**, and the only place testing is verified end-to-end in this plan. If a criterion can't be verified mechanically, mark it `(manual)` — the Supervisor will ask the user to confirm.

- AC-1: outcome. Verify: `tests/path/test_file.py::test_name` (written in Phase 1, re-run in Verification).
- AC-2: outcome. Verify: `tests/path/test_file.py::test_name`.
- AC-3 (manual): outcome. Verify: what the user looks at to confirm — no automated test, skipped in Phase 1.

On from-issue plans, these are lifted from the issue body and assigned `AC-N` IDs. On standalone plans, they come out of the grill. Architecture decisions below are derived from these criteria.

---

## Architecture decisions

Structural choices the user has made for this plan. Implementers MUST NOT deviate. If a task surfaces a structural choice not covered here, stop and surface it to the user before writing code.

**Files affected:**
- `path/to/file.py` — what changes
- `path/to/new_module/` — new

**Directory shape (after change):**

```
src/
  module/
    existing.py
    new_thing.py   ← new
```

**Decisions** (terse — sacrifice grammar for brevity):
- AD-1: decision. Why. (Principle: SRP / Pattern: Strategy / Convention: matches existing X)
- AD-2: decision. Why. (tag)

**Design principles in play:** cohesion target, coupling boundaries, encapsulation rules, SOLID/DRY/KISS dimensions that this change puts pressure on.

**Patterns:** GoF or architectural patterns used (e.g., Strategy in `handlers/`, layered separation between `api/` and `core/`), and any deliberately avoided with a one-line reason.

**Mock code snippet:**

A non-runnable sketch that shows every architectural/design choice made above in code form — class/function shapes, where each piece lives, dependency direction, public-vs-private surface, pattern wiring. The goal is one place a human or Claude can read to see the final shape before any task is implemented. Use file-name comments to anchor each block to its target location.

**Required for any plan that adds or edits code.** Skip only when the plan touches non-code artifacts exclusively (e.g., docs, `.md` files, prose-only changes).

```python
# src/module/new_thing.py
class NewThing:                       # AD-1: lives in module/, not core/
    def __init__(self, dep: Dep):     # AD-2: dependency injected, not imported
        self._dep = dep

    def run(self) -> Result:          # AD-3: public surface
        ...

# src/module/existing.py — extended, not duplicated (AD-4)
def existing_entry(...):
    thing = NewThing(dep=...)
    return thing.run()
```

---

## Phase 0 — Prerequisites

Phase 0 is an **interactive walkthrough** with the user, not an automated step. Each row is a confirmation, decision, or external prerequisite. The Supervisor walks the rows one at a time with the user; rows that need code (e.g., a quick check) may be handed to a `claude` subagent, but no test block runs against Phase 0. A row flips ✅ on user confirmation.

| Task | File | Status |
|------|------|--------|
| Description of prerequisite task | — | ⬜ |

---

## Phase 1 — Write acceptance tests

**This phase is mandatory and always second.** Write the actual failing (red) automated tests named in every non-`(manual)` `AC-N`'s verify clause, using the project's existing test framework and conventions. No implementation code — a test in this phase must fail because the behavior doesn't exist yet, never because of a broken test. Implementation phases below make these tests pass; Verification re-runs them as proof.

### Group 1 — [short name]

One line describing which `AC-N` tests this group writes and why they bundle together (shared test file or single atomic change).

**Architecture decisions (Group 1):** No architectural decisions apply. (Or: follows AD-N if it governs test placement/structure.)

| Task | File | Status |
|------|------|--------|
| Write test for AC-1 | [test_file.py](../tests/path/test_file.py) | ⬜ |
| Write test for AC-2 | [test_file.py](../tests/path/test_file.py) | ⬜ |

---

## Phase 2 — [Phase Name]

Brief description of what this phase delivers.

### Group 1 — [short name]

One line describing what this group changes and why these tasks bundle together (shared file or single atomic change).

**Architecture decisions (Group 1):** Follows AD-N ([short title]) and AD-N ([short title]). References ADR-NNNN ([short title]) where relevant.

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |
| Description of task | [filename](../path/to/file.py) | ⬜ |

### Group 2 — [short name]

One line describing this group.

**Architecture decisions (Group 2):** Follows AD-N ([short title]). (Or: no architectural decisions apply.)

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

---

## Phase 3 — [Phase Name]

Brief description of what this phase delivers.

### Group 1 — [short name]

One line describing this group.

**Architecture decisions (Group 1):** Follows AD-N ([short title]). (Or: no architectural decisions apply.)

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

---

## Phase N — Verification

**This phase is mandatory and always last. No new code is written here — verification only, and the single source of truth for testing this plan.** No other phase or Group carries a test block. On any failure, the Supervisor stops immediately and escalates to the user — no automatic retry, no fixed attempt cap; the user decides what happens next each time.

### Group 1 — Architecture sweep

| Task | File | Status |
|------|------|--------|
| Verify codebase matches every `AD-N` in `## Architecture decisions` | — | ⬜ |
| Verify code shape matches the mock code snippet | — | ⬜ |

**Checks:**
- Each `AD-N` is `[FOUND]` in the codebase with evidence (file:line).
- Each entry in `## Architecture decisions` → Files affected exists and matches its stated change.
- Directory shape matches the post-change tree.
- Mock snippet shape (class/function names, file locations, dependency direction, public surface) matches the implementation.
- No `[POSSIBLE VIOLATION]` of stated design principles or patterns.

### Group 2 — Acceptance criteria

| Task | File | Status |
|------|------|--------|
| Verify AC-1 | — | ⬜ |
| Verify AC-2 | — | ⬜ |
| Verify AC-3 (manual) | — | ⬜ |

**Checks:** one row per `AC-N` from `## Acceptance criteria` — re-run the exact test named in its `Verify:` line (written in Phase 1) and confirm it now passes green; `(manual)` rows are confirmed with the user instead. Auto-rendered from the AC section by the planner — do not edit independently.

---

## Claude Instructions

Context and constraints that help Claude implement this plan correctly:

- **Architecture binding:** Do not introduce structural choices (new modules, new patterns, new dependency directions, new cross-layer dependencies) not covered by `## Architecture decisions` above. If a task requires one, stop and surface it to the user before writing code — never improvise structure. Cite the relevant `AD-N` when a task implements a decision.
- **Conventions:** Naming, file structure, patterns to follow from the existing codebase (beyond what's already pinned in `## Architecture decisions`).
- **Constraints:** What NOT to do — things to avoid or stay in scope of.
- **Order dependency:** Any phases or tasks that must complete before others can start.
- **Testing:** `## Phase 1 — Write acceptance tests` writes the tests red; nothing is *verified* (i.e., no test is run and judged) until `## Phase N — Verification`, which re-runs those same tests and expects green. No Group or Phase before Verification carries a test/check block. Any Verification failure stops the plan immediately and goes to the user — there is no automatic retry.
</content>
