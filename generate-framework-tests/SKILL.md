---
name: generate-framework-tests
description: >
  Scaffold and maintain a project's framework-executable test suite through a
  guided, approval-gated workflow. Use when the user says "generate framework
  tests", "generate unit tests", "write tests for this", "add test coverage",
  "generate runnable tests", or "scaffold tests". Creates real tests runnable
  by pytest, vitest, jest, go test, cargo test, or JUnit Jupiter — not
  markdown scaffolds.
---

# generate-framework-tests

Guided skill for writing real, framework-executable test files. Every decision requires explicit approval before the skill advances. The skill writes plain code files that the project's test runner can execute directly — no frontmatter, no skill-specific markers.

## Invocation

- Slash command: `/generate-framework-tests`
- Natural-language triggers: "generate framework tests", "generate unit tests", "write tests for this", "add test coverage", "generate runnable tests", "scaffold tests"
- Optional path argument: a file path, directory path, or nothing (whole project). Examples:
  - `/generate-framework-tests src/auth.py` — scope to one file
  - `/generate-framework-tests src/` — scope to a directory
  - `/generate-framework-tests` — whole project (ask or infer)

---

## Stage 0 — Scope Parsing

Parse the optional path argument from the invocation:

- **File path given** — scope to that single file.
- **Directory path given** — scope to all source files inside that directory.
- **No argument** — check conversation context for a recently mentioned file or module. If one is clearly in scope, use it and state the assumption. If none is clear, ask the user: "Which file or directory should I generate tests for? Or should I cover the whole project?" Do not advance until scope is confirmed.

Once scope is determined, confirm it in one sentence before proceeding. Silence from the user is not confirmation — wait for an explicit "yes", "correct", or equivalent.

---

## Stage 1 — Manifest Check (fast exit)

On invocation, check for the manifest at `.generate-framework-tests/sidecar-manifest.json`.

If the manifest exists:

1. For each source file recorded in the manifest, compute its current SHA-256 hash and compare it to the stored hash.
2. Check whether any source files in scope are absent from the manifest (i.e. new untested files).
3. Consult `drift-detection.md` for the full comparison algorithm and hash format.

If all hashes match **and** no new untested source files exist within scope → print exactly:

> All tests are up to date — nothing to do.

Then stop. Do not proceed to detection or approval.

If any hash has changed, or any untested source file is found, proceed to Stage 2 with the changed/new files as the effective scope.

If no manifest exists, proceed to Stage 2 with the full confirmed scope.

---

## Stage 2 — Detection and Report

Detect the project language and appropriate test framework. Delegate the detection logic to `language-detection.md`, which specifies the signals to inspect (file extensions, config files, lock files, existing test files) and how to resolve ambiguity when multiple frameworks are present.

After detection, print a short report:

- Detected language and version (if determinable)
- Proposed test framework and the reason it was chosen
- Existing test directory layout (or "none found")
- List of source files in scope that have no corresponding test file, or whose test file is out of date per the manifest

Do not ask for approval here. This report is informational. Proceed directly to Stage 3.

---

## Stage 3 — Combined Approval Gate

Build the full plan and present it for a single approval before writing anything. Reference `plan-template.md` for the exact structure of the plan document to render.

The plan must include:

- **Framework choice** — the selected framework, with a one-line rationale.
- **Files to create** — each new test file path, with the source file it covers.
- **Files to update** — each existing test file that needs changes, annotated with drift notes (which cases are new, which are stale). Drift annotation logic is owned by `drift-detection.md`.
- **Per-file case list** — for each file, every test case: its name and a one-line statement of intent.

**Mini-confirm (new framework only):** If no test framework exists in the project yet, pause before building the full plan and ask: "No test framework detected. I'll set up [framework] — does that work, or would you prefer a different one?" Wait for a response before continuing plan construction.

Present the completed plan to the user and halt. Do not write any files until the user approves the plan with an explicit phrase ("approve", "looks good", "go ahead", or equivalent). Silence is not approval.

The user may inline-edit the plan before approving: add cases, remove cases, rename test files, drop files from scope, or re-scope entirely. Apply all edits to the internal plan before writing. Confirm that edits have been applied in a short acknowledgement, then re-present the affected section and ask for final approval.

---

## Stage 4 — Drift Handling

Before writing, reconcile the approved plan against any existing test files using `drift-detection.md`. That file owns the full drift algorithm; this skill does not duplicate it.

One invariant this skill enforces unconditionally:

**User-added test cases are never proposed for removal or change.** A user-added case is any case present in an existing test file that is not recorded in the manifest's `cases[]` array for that file. The manifest is the only source of truth for "did the skill write this case?" If a case is not in `cases[]`, treat it as user-owned and leave it untouched.

Proceed to Stage 5 only after drift reconciliation is complete.

---

## Stage 5 — Write and Run

Write the approved test files. Each file must be plain, framework-executable source code with no YAML frontmatter, no skill-specific markers, and no embedded metadata. The file must be runnable by the project's test command without modification.

After writing, update `.generate-framework-tests/sidecar-manifest.json` with the new manifest state: source file paths, their SHA-256 hashes, and the `cases[]` array for each test file (recording only the cases this skill wrote). Manifest format and field names are specified in `drift-detection.md`.

Then run only the just-written or just-updated test files using the project's scoped test command. Do not run the full suite. Do not install toolchains or package managers. Three outcomes:

- **All pass** — print a short pass summary (number of tests, files covered).
- **Failures** — print the failure output verbatim. Do not retry, do not auto-fix.
- **Failed to execute** — print the error output verbatim. Do not retry, do not auto-fix.

In all three outcomes, stop after printing. Do not re-enter the approval loop or propose additional changes.

---

## Bundled Files

The three files below are bundled with this skill. Each owns a specific domain. SKILL.md references them by name and role; their content is not duplicated here.

| File | Role |
|---|---|
| `language-detection.md` | Specifies how to detect the project language and select the appropriate test framework: which signals to inspect, how to handle ambiguity, and framework-specific conventions to follow. |
| `plan-template.md` | Defines the exact structure and formatting of the plan presented at Stage 3, including how to render framework choice, file lists, drift annotations, and per-file case tables. |
| `drift-detection.md` | Owns the manifest schema, SHA-256 hashing algorithm, drift comparison logic, and the rules for which cases count as user-owned vs. skill-owned. |

---

## Constraints

- Generated test files must be plain framework-executable code. No YAML frontmatter, no skill markers, no embedded metadata of any kind.
- The manifest path is always `.generate-framework-tests/sidecar-manifest.json`. It is never placed elsewhere.
- User-added test cases (those absent from the manifest's `cases[]`) are never proposed for removal or change.
- Approval is always explicit. "approve", "looks good", "go ahead", or equivalent. Silence does not advance the workflow.
- The skill does not install toolchains, package managers, or test runners. If the project's test command cannot execute, surface the error and stop.
- The skill does not retry failing tests or auto-fix test failures. Failures are reported and the skill stops.
- This is a markdown-only skill. There are no compiled artifacts, executables, or code files in the skill bundle itself.
- Do not modify files in `generate-test/` or `run-tests/`.
