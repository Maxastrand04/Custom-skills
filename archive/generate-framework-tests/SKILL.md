---
name: generate-framework-tests
description: Scaffolds and maintains real runnable tests for pytest, vitest, jest, go test, cargo test, or JUnit. A sidecar manifest gives fast-exit when nothing changed and drift-diff when it did. Never touches user-added cases.
disable-model-invocation: true
---

# generate-framework-tests

Writes real, framework-executable test files, meaning plain source the project's test runner executes directly, with no frontmatter or skill markers.

The skill advances through **gates**. A gate opens only on an explicit affirmative from the user, meaning "yes", "approve", "looks good", or equivalent. Silence never advances it.

## Stage 0: Scope

Resolve the optional path argument:

- **File path.** Scope to that file.
- **Directory path.** Scope to source files under it.
- **No argument.** Check the conversation for a file clearly in scope. If one is found, use it and state the assumption. Otherwise ask: "Which file or directory should I generate tests for, or the whole project?"

Confirm the scope in one sentence. This is a **gate**.

## Stage 1: Fast-exit

`drift-detection.md` owns the manifest and the fast-exit rule. Run its fast-exit check against the confirmed scope.

If it reports every in-scope source unchanged and none untested, print exactly:

> All tests are up to date, nothing to do.

Then stop. Otherwise continue with the changed and untested files as the effective scope.

## Stage 2: Detect and report

`language-detection.md` owns language and framework detection, including the mirror-existing-convention rule. Detect, then print a short **informational** report. Do not gate here.

- Detected language and version, if determinable
- Proposed framework and a one-line reason
- Existing test layout, or "none found"
- In-scope source files with no current test

Proceed directly to Stage 3.

## Stage 3: Plan and approval gate

Build the full plan per `plan-template.md`, computing drift for existing test files via `drift-detection.md`. The plan covers framework choice with rationale, files to create, files to update with drift notes, and the per-file case list.

**New-framework mini-gate:** if the project has no test framework, ask "No test framework detected. Set up [framework], or name another?" before building the plan.

Present the plan and stop. This is the approval **gate**. The user may inline-edit it, adding, removing, or renaming cases, and dropping or re-scoping files. Apply the edits, re-present the affected section, and gate again.

## Stage 4: Write and run

Write the approved files as plain framework-executable code, with no frontmatter and no skill markers, runnable by the project's test command unmodified.

Enforce **user-added-case immunity** and update the manifest, both per `drift-detection.md`. Cases the user added, meaning those absent from the manifest's `cases[]`, are never moved, changed, or removed.

Then run only the just-written and just-updated files with the project's scoped command. Never run the full suite, and never install toolchains. Report the outcome and stop; do not retry, auto-fix, or re-open a gate:

- **Pass.** A short summary giving the test count and the files covered.
- **Failure or execution error.** Print the output verbatim.

## Bundled files

- `language-detection.md` holds language and framework detection, the mirror-existing-convention rule, and per-language placement and test commands.
- `plan-template.md` holds the structure of the Stage 3 approval plan.
- `drift-detection.md` holds the manifest schema, fast-exit rule, drift diff, user-added-case immunity, orphan handling, and manifest writes.
