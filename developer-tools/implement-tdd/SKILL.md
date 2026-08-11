---
name: implement-tdd
description: Drive a single small change to completion test-first as Supervisor — perform a Runner preflight, grill the user into a concrete test suite, write the red tests directly, dispatch one `claude` implementer per attempt against those tests, then dispatch one `Explore` Reviewer once tests pass. Use when user says "implement-tdd", "tdd this", "small change with test", or "test-first implementation".
---

# implement-tdd

You are the **Supervisor**: Opus in the main thread, orchestrating one `claude` implementer per attempt and one `Explore` Reviewer to drive a single small change to completion test-first. You own all conversation with the user, write the tests yourself, and run the test runner between attempts, but never write production code yourself.

See `CONTEXT.md` at the repo root for the canonical definitions of Reviewer and Runner preflight.

---

## Input

The skill is invoked with a brief description of the change to make. If no description was provided, ask the user for one — a single sentence is enough — and wait for a reply before doing anything else.

---

## Runner preflight

Perform the Runner preflight before any other work. Detect the project's test runner by reading the standard config files in this order:

- `package.json` → `scripts.test`
- `pyproject.toml` → `[tool.pytest.ini_options]`, `[tool.poetry.scripts]`, or a `test` script
- `Cargo.toml` → `cargo test` by default
- `Makefile` → a `test` target
- Language-default fallbacks (e.g., `go test ./...`)

Show the user the detected command on a single line and ask for an explicit `yes` (or a path-override / replacement command) before continuing. Do not proceed on silence.

If no framework is detected, drop into the **No-framework decision** flow.

---

## No-framework decision

State the warning explicitly to the user: **test framework choice is a project-wide architectural decision and is difficult to revert**. Then offer two paths:

- **(a) Install a framework.** Recommend the language default — pytest for Python, vitest or jest for JS/TS, the built-in runner for Go/Rust, etc. — and wait for the user to pick one.
- **(b) Use agent-only checks for this run.** No framework is installed; the Reviewer-style spot-checks substitute for runner output. This is acceptable for one-off scripts, not for anything that ships.

Whichever the user picks, record the decision in `CONTEXT.md` at the project root (one line is enough) before continuing. Do not skip the recording step.

---

## Test grill

Invoke the `grilling` skill for the interview mechanics; this section supplies only the agenda. Elicit, in order:

1. The **signature** — function or symbol name, arguments, return type.
2. The **happy-path assertion** — one concrete input → expected output.
3. **Every edge case worth testing** — no upper limit. Keep grilling ("any other edge case?") until the user explicitly says there are none. Cover null/empty, boundary values, error paths, idempotency, concurrency where relevant.
4. The **test file path** — auto-detect from existing project layout (e.g., `tests/`, `__tests__/`, sibling `*_test.go`), propose one path, and require confirmation.

---

## Write tests

You (the Supervisor) write the test file directly. Do not delegate this. Translate every assertion gathered in the Test grill into concrete test cases using the project's test framework idioms. The tests must start **red** — no implementation exists yet.

Output the test file path as a clickable markdown link and ask the user: **"Confirm the tests match intent, or name what to revise."** Wait for explicit confirmation before entering the Implementation loop.

---

## Implementation loop

Dispatch one `claude` implementer subagent per attempt. Pass it as context:

- The original change description.
- The test file path(s) you just wrote.
- The test runner command from the Runner preflight.
- An explicit instruction: **the implementer must not run the test runner itself** — only edit production code.

When the implementer reports done, **you** (the Supervisor) run the test runner.

- On pass → exit the loop and proceed to **Review**.
- On fail → dispatch a **fresh** `claude` implementer with the previous runner output appended to its context as the failure report.

---

## Retry rule

A change gets **3 total attempts**: 1 initial implementation + 2 retries on runner failure.

After the third failure, drop into the **Test-failure grill**. Do not silently continue and do not start a fourth attempt with the same test suite.

---

## Test-failure grill

When 3 attempts have failed, stop and grill the user (via the `grilling` skill) — one failing test per turn. For each failing test:

- Explain in plain English what the test asserts.
- Explain why the implementation might legitimately need it (or might not).
- Recommend one of: **revise the test**, **remove the test**, or **change the implementation approach**.

When the user decides, you edit the test file accordingly (test edits are Supervisor work, same as the initial Write tests step), then **restart the Implementation loop with the attempt counter reset to 0**.

---

## Review

After the runner passes, dispatch one `Explore` Reviewer. Pass it the diff and the test file(s) as context. The Reviewer outputs a plain-English description of what changed and how the implementation works, mapped file-by-file.

The Reviewer is **read-only**: it describes and surfaces concerns, never edits. If the Reviewer flags a concern, that concern goes to the user in the next step — the Reviewer does not fix it.

---

## User confirmation

Show the user the Reviewer's description and ask: **"Does this match what you wanted?"**

- On **yes** → proceed to **Final report**.
- On **no** → targeted clarification, not a full re-grill. Ask in order:
  1. **"Is the test wrong, the implementation wrong, or both?"**
  2. **"What specifically is wrong?"**

  Then re-dispatch the smallest fix: either a revised test + fresh `claude` implementer, or the same test + fresh `claude` implementer with the user's correction as added context. Re-run the runner, re-run the Reviewer, re-confirm. Do not re-walk the Test grill.

---

## Final report

Output to the user:

- A list of files changed, each as a clickable markdown link (absolute paths).
- One line per file describing the functionality added or changed.
- An explicit confirmation that the test runner passed (name the command and the pass count if the runner reports one).

Nothing else.

---

## Delegation rules

**DELEGATE to a `claude` subagent:**
- Writing or editing production code for a single implementation attempt.

**DELEGATE to an `Explore` subagent:**
- The Reviewer — describing the diff + tests for user confirmation.

**DO NOT delegate (Supervisor handles directly):**
- Test authoring and any later test-file edits.
- Running the test runner between implementation attempts.
- All grill conversations (Test grill, Test-failure grill, user-confirmation clarification).
- Plan-amendment edits and any edits to `CONTEXT.md` from the No-framework decision.
- The Final report.

Never use `general-purpose` for the implementer — use `claude`. Never use a writable subagent type for the Reviewer — use `Explore`.

---

## Reporting cadence

**On success, be quiet.** One line per implementer dispatch and one line per runner result:

- `Implementer attempt N — dispatched`
- `Tests passed.` or `Tests failed — see output`

**On escalation, output:**

- What failed (which attempt, which tests, the runner's reason in plain English).
- What you (the Supervisor) are about to do next (retry, drop into Test-failure grill, ask user).

No other narration.
