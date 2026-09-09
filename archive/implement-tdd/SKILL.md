---
name: implement-tdd
description: The small-change bypass around the kanban board. Grills a test suite, writes the red tests, dispatches one implementer per attempt, then one reviewer on green.
disable-model-invocation: true
---

# implement-tdd

You are the **Supervisor**: Opus in the main thread, orchestrating one `claude` implementer per attempt and one `Explore` Reviewer to drive a single small change to completion test-first. You own all conversation with the user, write the tests yourself, and run the test runner between attempts, but never write production code yourself.

See `CONTEXT.md` at the repo root for the canonical definitions of Reviewer and Runner preflight.

---

## Input

The skill is invoked with a brief description of the change to make. If no description was provided, ask the user for one, since a single sentence is enough, and wait for a reply before doing anything else.

---

## Runner preflight

Perform the Runner preflight before any other work. Detect the project's test runner by reading the standard config files in this order:

- `package.json`, at `scripts.test`
- `pyproject.toml`, at `[tool.pytest.ini_options]`, `[tool.poetry.scripts]`, or a `test` script
- `Cargo.toml`, giving `cargo test` by default
- `Makefile`, at a `test` target
- Language-default fallbacks, such as `go test ./...`

Show the user the detected command on a single line and ask for an explicit `yes`, or a path override or replacement command, before continuing. Do not proceed on silence.

If no framework is detected, drop into the **No-framework decision** flow.

---

## No-framework decision

State the warning explicitly to the user: **test framework choice is a project-wide architectural decision and is difficult to revert**. Then offer two paths:

- **(a) Install a framework.** Recommend the language default, meaning pytest for Python, vitest or jest for JS and TS, and the built-in runner for Go and Rust. Wait for the user to pick one.
- **(b) Use agent-only checks for this run.** No framework is installed; the Reviewer-style spot-checks substitute for runner output. This is acceptable for one-off scripts, not for anything that ships.

Whichever the user picks, record the decision in `CONTEXT.md` at the project root, where one line is enough, before continuing. Do not skip the recording step.

---

## Test grill

Invoke the `grilling` skill for the interview mechanics; this section supplies only the agenda. Elicit, in order:

1. The **signature**, meaning the function or symbol name, its arguments, and its return type.
2. The **happy-path assertion**, meaning one concrete input and the expected output.
3. **Every edge case worth testing**, with no upper limit. Keep asking "any other edge case?" until the user explicitly says there are none. Cover null and empty values, boundary values, error paths, idempotency, and concurrency where relevant.
4. The **test file path**. Auto-detect it from the existing project layout, such as `tests/`, `__tests__/`, or a sibling `*_test.go`, propose one path, and require confirmation.

---

## Write tests

You (the Supervisor) write the test file directly. Do not delegate this. Translate every assertion gathered in the Test grill into concrete test cases using the project's test framework idioms. The tests must start **red**, since no implementation exists yet.

Output the test file path as a clickable markdown link and ask the user: **"Confirm the tests match intent, or name what to revise."** Wait for explicit confirmation before entering the Implementation loop.

---

## Implementation loop

Dispatch one `claude` implementer subagent per attempt. Pass it as context:

- The original change description.
- The test file path(s) you just wrote.
- The test runner command from the Runner preflight.
- An explicit instruction that **the implementer must not run the test runner itself** and may only edit production code.

When the implementer reports done, **you** (the Supervisor) run the test runner.

- On a pass, exit the loop and proceed to **Review**.
- On a failure, dispatch a **fresh** `claude` implementer with the previous runner output appended to its context as the failure report.

---

## Retry rule

A change gets **3 total attempts**: one initial implementation plus two retries on runner failure.

After the third failure, drop into the **Test-failure grill**. Do not silently continue and do not start a fourth attempt with the same test suite.

---

## Test-failure grill

When 3 attempts have failed, stop and grill the user, via the `grilling` skill, one failing test per turn. For each failing test:

- Explain in plain English what the test asserts.
- Explain why the implementation might legitimately need it, or might not.
- Recommend one of three: **revise the test**, **remove the test**, or **change the implementation approach**.

When the user decides, you edit the test file accordingly, since test edits are Supervisor work like the initial Write tests step, then **restart the Implementation loop with the attempt counter reset to 0**.

---

## Review

After the runner passes, dispatch one `Explore` Reviewer. Pass it the diff and the test file(s) as context. The Reviewer outputs a plain-English description of what changed and how the implementation works, mapped file-by-file.

The Reviewer is **read-only**: it describes and surfaces concerns, never edits. If the Reviewer flags a concern, that concern goes to the user in the next step. The Reviewer does not fix it.

---

## User confirmation

Show the user the Reviewer's description and ask: **"Does this match what you wanted?"**

- On **yes**, proceed to **Final report**.
- On **no**, run a targeted clarification, not a full re-grill. Ask in order:
  1. **"Is the test wrong, the implementation wrong, or both?"**
  2. **"What specifically is wrong?"**

  Then re-dispatch the smallest fix: either a revised test with a fresh `claude` implementer, or the same test with a fresh `claude` implementer carrying the user's correction as added context. Re-run the runner, re-run the Reviewer, re-confirm. Do not re-walk the Test grill.

---

## Final report

Output to the user:

- A list of files changed, each as a clickable markdown link with an absolute path.
- One line per file describing the functionality added or changed.
- An explicit confirmation that the test runner passed, naming the command and the pass count if the runner reports one.

Nothing else.

---

## Recorded decisions

This skill does not survey `docs/adr/`. It is the small-change bypass, and `refactor-ticket` is where a diff gets read against the whole set. But ADRs bind here as much as anywhere, so when one surfaces during the run, in the Test grill, in the Reviewer's output, or in a file you are about to touch:

- **A decision the change would breach** stops the change, not the decision. Take the compliant approach instead.
- **A decision that looks stale**, meaning the code it governs has moved on or the trade-off in its Reason no longer holds, is still binding. Note it to the user in one line, naming the ADR and why it looks stale.

Either way, **you never edit a file in `docs/adr/`**. Changing one takes a full `/challenge-adr` session, and only the user can start it. Say so, and let them decide whether to break off and run it. Never assume a challenge would succeed and build as though it already had.

---

## Delegation rules

Writing production code and running the Reviewer pass are the only work that leaves your hands. **You handle everything else directly:**
- Test authoring and any later test-file edits.
- Running the test runner between implementation attempts.
- All grill conversations, meaning the Test grill, the Test-failure grill, and the user-confirmation clarification.
- Plan-amendment edits and any edits to `CONTEXT.md` from the No-framework decision.
- Naming a breached or stale ADR to the user. Never editing one.
- The Final report.

Never use `general-purpose` for the implementer; use `claude`. Never use a writable subagent type for the Reviewer; use `Explore`.

---

## Reporting cadence

**On success, be quiet.** One line per implementer dispatch and one line per runner result:

- `Implementer attempt N: dispatched`
- `Tests passed.` or `Tests failed, see output`

**On escalation, output:**

- What failed, naming the attempt, the tests, and the runner's reason in plain English.
- What you, the Supervisor, are about to do next, meaning retry, drop into the Test-failure grill, or ask the user.

No other narration.
