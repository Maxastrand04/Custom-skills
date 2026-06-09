# N.N — Plan Name

One sentence describing what this plan accomplishes.

**Goal:** What the completed plan should achieve — the concrete outcome or capability that will exist when all phases are done.

**Status legend:**  ⬜ Not started · 🟡 In progress · ✅ Done

---

## Acceptance criteria

What "done" means for this plan, expressed as a numbered list of verifiable criteria. **This is the contract the final Verification phase tests against.** If a criterion can't be verified mechanically, mark it `(manual)` — the Supervisor will ask the user to confirm.

- **AC-1 — [Short title]** — The observable outcome.
  *Verify by:* concrete check (command, behavior, file/symbol presence, HTTP response, screenshot, etc.).
- **AC-2 — [Short title]** — The observable outcome.
  *Verify by:* concrete check.
- **AC-3 — [Short title]** *(manual)* — The observable outcome.
  *Verify by:* what the user needs to look at to confirm.

On from-issue plans, these are lifted verbatim from the issue body and assigned `AC-N` IDs. On standalone plans, they are produced during the grill. Architecture decisions below should be derived from these criteria.

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

**Decisions:**
- **AD-1 — [Short title]** — The decision. *Rationale.* *(Principle: SRP / Pattern: Strategy / Convention: matches existing X)*
- **AD-2 — [Short title]** — The decision. *Rationale.* *(Principle / Pattern / Convention tag.)*

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

Phase 0 is an **interactive walkthrough** with the user, not an automated step. Each row is a confirmation, decision, or external prerequisite. The Supervisor walks the rows one at a time with the user; rows that need code (e.g., a quick check) may be handed to a `claude` subagent, but no Group tester or Phase tester runs against Phase 0. A row flips ✅ on user confirmation.

| Task | File | Status |
|------|------|--------|
| Description of prerequisite task | — | ⬜ |

---

## Phase 1 — [Phase Name]

Brief description of what this phase delivers.

### Group 1 — [short name]

One line describing what this group changes and why these tasks bundle together (shared file or single atomic change).

**Architecture decisions (Group 1):**
- Follows AD-N ([short title]) and AD-N ([short title]).
- References ADR-NNNN ([short title]) where relevant.

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |
| Description of task | [filename](../path/to/file.py) | ⬜ |

**Functionality tests / checks (Group 1):**
- AC-N: concrete check verifying the Group satisfies this criterion (command, file/symbol presence, HTTP response, etc.)
- AC-N: another check

**Architecture tests / checks (Group 1):**
- (subagent) AD-N present in `path/to/file.py` — verify shape.
- (human) AD-N — no new import from `core/` into `handlers/`.

### Group 2 — [short name]

One line describing this group.

**Architecture decisions (Group 2):**
- Follows AD-N ([short title]).
- No architectural decisions apply (or list the relevant AD-N items).

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

**Functionality tests / checks (Group 2):**
- AC-N: concrete check verifying the Group satisfies this criterion
- AC-N: another check

**Architecture tests / checks (Group 2):**
- (subagent) AD-N conformance check — verify structure in `path/to/file.py`.

### Functionality tests / checks (Phase 1 — integration)

Cross-group checks the Phase tester runs after all groups in this phase are ✅. These verify the `AC-N` criteria that span multiple Groups; they are not a re-run of the per-group checks.

- AC-N: cross-group check verifying the criterion spanning Group 1 + Group 2
- AC-N: another cross-group check

### Architecture tests / checks (Phase 1 — integration)

Cross-group structural checks. The architecture reviewer (subagent or human) verifies that the composed result respects all AD-N decisions across both Groups.

- (subagent) Composed code respects AD-N dependency direction across both Groups.
- (human) No top-level section renamed; additive-only changes verified.

---

## Phase 2 — [Phase Name]

Brief description of what this phase delivers.

### Group 1 — [short name]

One line describing this group.

**Architecture decisions (Group 1):**
- Follows AD-N ([short title]).
- No architectural decisions apply (or list the relevant AD-N items).

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

**Functionality tests / checks (Group 1):**
- AC-N: concrete check verifying the Group satisfies this criterion

**Architecture tests / checks (Group 1):**
- (subagent) AD-N conformance check — verify structure in `path/to/file.py`.

### Functionality tests / checks (Phase 2 — integration)

- AC-N: cross-group check verifying the criterion that spans both Groups

### Architecture tests / checks (Phase 2 — integration)

- (subagent) Composed code respects AD-N dependency direction.

---

## Phase N — Verification

**This phase is mandatory and always last. No new code is written here — verification only.** If any check fails, the Supervisor escalates to the user; nothing is auto-fixed.

### Group 1 — Architecture sweep

| Task | File | Status |
|------|------|--------|
| Verify codebase matches every `AD-N` in `## Architecture decisions` | — | ⬜ |
| Verify code shape matches the mock code snippet | — | ⬜ |

**Tests / checks (Group 1):**
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

**Tests / checks (Group 2):**
- One row per `AC-N` from `## Acceptance criteria`, each tested by the `Verify by:` line in that section. Auto-rendered from the AC section by the planner — do not edit independently.

### Tests / checks (Phase N — integration)

- All `AC-N` `[PASS]` and all `AD-N` `[FOUND]`, with no outstanding `[POSSIBLE VIOLATION]` or unresolved `[MANUAL CHECK REQUIRED]`.

---

## Claude Instructions

Context and constraints that help Claude implement this plan correctly:

- **Architecture binding:** Do not introduce structural choices (new modules, new patterns, new dependency directions, new cross-layer dependencies) not covered by `## Architecture decisions` above. If a task requires one, stop and surface it to the user before writing code — never improvise structure. Cite the relevant `AD-N` when a task implements a decision.
- **Conventions:** Naming, file structure, patterns to follow from the existing codebase (beyond what's already pinned in `## Architecture decisions`).
- **Constraints:** What NOT to do — things to avoid or stay in scope of.
- **Order dependency:** Any phases or tasks that must complete before others can start.
- **Testing:** How to verify each phase works before moving on.
