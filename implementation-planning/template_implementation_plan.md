# N.N — Plan Name

One sentence describing what this plan accomplishes.

**Goal:** What the completed plan should achieve — the concrete outcome or capability that will exist when all phases are done.

**Status legend:**  ⬜ Not started · 🟡 In progress · ✅ Done

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

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |
| Description of task | [filename](../path/to/file.py) | ⬜ |

**Tests / checks (Group 1):**
- Concrete check the Group tester will run (command, file/symbol presence, HTTP response, etc.)
- Another concrete check

### Group 2 — [short name]

One line describing this group.

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

**Tests / checks (Group 2):**
- Concrete check
- Another concrete check

### Tests / checks (Phase 1 — integration)

Cross-group checks the Phase tester runs after all groups in this phase are ✅. These verify the groups compose correctly; they are not a re-run of the per-group checks.

- Integration check spanning Group 1 + Group 2
- Another integration check

---

## Phase 2 — [Phase Name]

Brief description of what this phase delivers.

### Group 1 — [short name]

| Task | File | Status |
|------|------|--------|
| Description of task | [filename](../path/to/file.py) | ⬜ |

**Tests / checks (Group 1):**
- Concrete check

### Tests / checks (Phase 2 — integration)

- Integration check

---

## Claude Instructions

Context and constraints that help Claude implement this plan correctly:

- **Architecture:** How the pieces fit together and why.
- **Conventions:** Naming, file structure, patterns to follow from the existing codebase.
- **Constraints:** What NOT to do — things to avoid or stay in scope of.
- **Order dependency:** Any phases or tasks that must complete before others can start.
- **Testing:** How to verify each phase works before moving on.
