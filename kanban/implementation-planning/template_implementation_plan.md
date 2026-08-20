# N.N — Plan Name

One sentence describing what this plan accomplishes.

**Goal:** The concrete outcome or capability that exists when all phases are done.

**Branch:** Branch the implementer works from.

**Status legend:**  ⬜ Not started · 🟡 In progress · ✅ Done

---

## Acceptance criteria

What "done" means, terse — sacrifice grammar for brevity. **The contract the final Verification phase tests against**, and what `Phase 1 — Red` reads to work out what each named test asserts. A criterion that can't be verified mechanically is marked `(manual)` and confirmed with the user instead.

- AC-1: outcome. Verify: `tests/path/test_file.py::test_name`.
- AC-2: outcome. Verify: `tests/path/test_file.py::test_name`.
- AC-3 (manual): outcome. Verify: what the user looks at to confirm.

---

## Public interface

**The contract, settled with the user and binding on the implementer.** Implement exactly these names, parameters, and return values — never rename, re-order, add, or drop one while implementing. If the contract itself proves wrong, stop and take it back to the user rather than changing it in code.

Everything *behind* it is the implementer's call — helpers, control flow, data structures, extra private modules. No implementation choice needs approval; the code-review session cleans up what's inside the boundary.

One block per file. `Phase 2 — Green` copies each stub in verbatim and fills the body.

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

## Phase 0 — Preflight

Only genuine **blockers** that must clear before execution starts — an external credential, a created resource, a decision that can't be made until execution time. Not an assumption-confirmation checklist. A lone `None` row means execution goes straight to Red.

| Task | File | Status |
|------|------|--------|
| None — no blockers | — | ✅ |

---

## Phase 1 — Red

**Mandatory, always second.** Write these tests failing, in the project's existing framework. No implementation code — a test here must fail because the behavior doesn't exist yet, never because the test is broken.

The rows name *what to write and where*, not what to assert: for each, find the `AC-N` whose `Verify:` clause names that test and derive the assertions from that criterion. Call the code through `## Public interface` exactly as written.

| Test function | File | Status |
|---------------|------|--------|
| `test_admin_redirect` | [test_login.py](../tests/path/test_login.py) | ⬜ |
| `test_expired_code_rejected` | [test_login.py](../tests/path/test_login.py) | ⬜ |

---

## Phase 2 — Green: [Phase Name]

What this phase delivers. Green phases make the Red tests pass — add as many as the work needs.

| Task | File | Status |
|------|------|--------|
| Implement `exchange_code` — copy its stub from `## Public interface`, fill the body | [oauth.py](../src/auth/oauth.py) | ⬜ |
| Description of task | [filename](../path/to/file.py) | ⬜ |

---

## Phase N — Verification

**Mandatory, always last. No new code.** One row per `AC-N`: re-run the exact test named in its `Verify:` line and confirm it now passes green; `(manual)` rows are confirmed with the user. The only place tests run — code quality is judged separately, against the committed diff.

| Task | File | Status |
|------|------|--------|
| Verify AC-1 | — | ⬜ |
| Verify AC-2 | — | ⬜ |
| Verify AC-3 (manual) | — | ⬜ |

---

## Claude Instructions

- **Conventions:** Naming, file structure, patterns to follow from the existing codebase.
- **Constraints:** What NOT to do — things to avoid or stay in scope of.
- **Order dependency:** Any phases or tasks that must complete before others can start.
- **Testing:** Nothing is run and judged until `## Phase N — Verification`, which re-runs the Phase-1 tests rather than inventing new checks. Any failure stops the plan and goes to the user.
