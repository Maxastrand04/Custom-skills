# N.N: Plan Name

One sentence describing what this plan accomplishes.

**Goal:** The concrete outcome or capability that exists when all phases are done.

**Branch:** Branch the implementer works from.

**Status legend:**  ⬜ Not started · 🟡 In progress · ✅ Done

---

## Acceptance criteria

What "done" means, terse. Sacrifice grammar for brevity. **The contract Verification tests against**, and what `Phase 1: Red` reads to work out what each named test asserts. A criterion that can't be verified mechanically is marked `(manual)` and confirmed with the user instead.

- AC-1: outcome. Verify: `tests/path/test_file.py::test_name`.
- AC-2: outcome. Verify: `tests/path/test_file.py::test_name`.
- AC-3 (manual): outcome. Verify: what the user looks at to confirm.

---

## Public interface

**The contract, settled with the user and binding on the implementer.** Implement exactly these names, parameters, and return values. Never rename, re-order, add, or drop one while implementing. If the contract itself proves wrong, stop and take it back to the user rather than changing it in code.

Everything *behind* it is the implementer's call, including helpers, control flow, data structures, and extra private modules. No implementation choice needs approval; the code-review session cleans up what's inside the boundary.

One block per file. `Phase 2: Green` copies each stub in verbatim and fills the body.

**`src/auth/oauth.py`**

```python
def exchange_code(code: str, redirect_uri: str) -> Session:
    """Exchange an OAuth authorization code for a logged-in session.

    `redirect_uri` must match the one the code was issued against.
    Returns a Session whose `.user` is the admin identified by the code's subject.
    Raises AuthError if the code is expired, already redeemed, or the URI mismatches.
    """
    raise NotImplementedError
```

---

## Phase 0: Prerequisites

**The pillars this plan stands on.** One row per module, function, feature, file, fixture, or external resource the implementation relies on but does not build. The implementer confirms every row before writing a single test, so a missing or broken row halts the plan: it has to be implemented or fixed first.

Rows say **what** has to exist and work, never how to check it. Choosing the check is the implementer's call in Phase 0, and the row's verb sets the bar: *exists* is settled by finding it, *works* is not. Not a list of what this plan builds, and not an assumption-confirmation checklist.

| Prerequisite | Where | Status |
|---|---|---|
| `Session` model exposes a `.user` relation | [session.py](../src/models/session.py) | ⬜ |
| `User` carries an admin flag | [user.py](../src/models/user.py) | ⬜ |
| Login redirect flow works end to end | [auth/](../src/auth/) | ⬜ |
| `authed_client` fixture builds a logged-in test client | [conftest.py](../tests/conftest.py) | ⬜ |
| `httpx` installed | [pyproject.toml](../pyproject.toml) | ⬜ |
| OAuth app credentials available | environment | ⬜ |

If the implementation stands on nothing that isn't already shipped and working, write a single row reading `None`.

---

## Phase 1: Red

**Mandatory, always second.** Write these tests in the project's existing framework, then run them and confirm every one fails. No implementation code. A test here must fail because the behavior doesn't exist yet, never because the test is broken, so a test that passes or errors on a typo halts the phase until it's fixed.

The rows name *what to write and where*, not what to assert. For each, find the `AC-N` whose `Verify:` clause names that test and derive the assertions from that criterion. Call the code through `## Public interface` exactly as written.

| Test function | File | Status |
|---------------|------|--------|
| `test_admin_redirect` | [test_login.py](../tests/path/test_login.py) | ⬜ |
| `test_expired_code_rejected` | [test_login.py](../tests/path/test_login.py) | ⬜ |

---

## Phase 2: Green: [Phase Name]

What this phase delivers. Green phases make the Red tests pass. Add as many as the work needs. A Verification failure comes back here, reopening only the rows the failure implicates.

| Task | File | Status |
|------|------|--------|
| Implement `exchange_code`, copying its stub from `## Public interface` and filling the body | [oauth.py](../src/auth/oauth.py) | ⬜ |
| Description of task | [filename](../path/to/file.py) | ⬜ |

---

## Phase N: Verification

**Mandatory, always last. No new code.** One row per `AC-N`: run the exact test named in its `Verify:` line and confirm it passes green. Every row runs, so failures surface as a set rather than one at a time. `(manual)` rows are confirmed with the user.

**Any failure sends the plan back to a Green phase**, and Green and Verification repeat until every row is green. Code quality is judged separately, against the committed diff.

| Task | File | Status |
|------|------|--------|
| Verify AC-1 | TBD | ⬜ |
| Verify AC-2 | TBD | ⬜ |
| Verify AC-3 (manual) | TBD | ⬜ |

---

## Claude Instructions

- **Conventions.** Naming, file structure, and patterns to follow from the existing codebase.
- **Constraints.** What NOT to do, meaning things to avoid or stay in scope of.
- **Order dependency.** Any phases or tasks that must complete before others can start.
- **Testing.** Tests run in three places and nowhere else: confirming a Phase 0 prerequisite, the end of `Phase 1: Red` to confirm every new test fails, and `## Phase N: Verification`. Verification re-runs the Phase-1 tests rather than inventing new checks, and a failure loops back to Green.
