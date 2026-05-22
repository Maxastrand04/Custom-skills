# Test Result

**X of Y passed** — e.g. `3 of 4 passed`

This file is rendered by the `run-tests` skill into `/tests/test-result.md` after every run. It consolidates the outcome of each test agent dispatched across all test spec files.

The top line above is the headline summary. Replace `X` with the number of agents whose status is `pass`, and `Y` with the total number of agents dispatched.

Status values are exactly one of: `pass`, `fail`, `timeout`.

---

## tests/foo.test.md

One `##` section per test spec file under `/tests/`. The header is the relative path to that spec file.

### Agent: unit

- pass

### Agent: integration

**Status:** fail
**Summary:** `parseConfig` rejected a valid YAML document because the top-level `version` key was treated as required when it is documented as optional.
**Repro:**
1. Check out the source at the SHA recorded in the spec frontmatter.
2. Run the integration agent against `tests/foo.test.md`.
3. Observe the assertion failure on the "optional version key" case.

---

## tests/bar.test.md

### Agent: behavior

**Status:** timeout
**Summary:** The behavior agent exceeded the per-agent wall-clock budget while waiting for the dev server to respond on port 3000.
**Repro:**
1. Start the project's dev server.
2. Run the behavior agent against `tests/bar.test.md`.
3. Observe that the agent hangs on the first network call and is killed after the timeout window.

---

## Entry conventions

- **Pass entries** are a single bullet line: `- pass`. No other fields are required.
- **Fail and timeout entries** must include all three fields:
  - `**Status:**` — one of `pass`, `fail`, `timeout`.
  - `**Summary:**` — one or two sentences of plain English describing what went wrong.
  - `**Repro:**` — an ordered list of concrete steps a human can follow to reproduce the failure locally.
- Agent sub-headers use `### Agent: <job>` where `<job>` matches the job name from the source spec file.
