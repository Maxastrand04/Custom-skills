---
name: generate-test
description: >
  Scaffold and maintain a project's test suite through a guided, approval-gated
  workflow. Use when the user says "generate tests", "build out the test plan",
  "scaffold test structure", "write tests for this", "add test coverage",
  "create test files", or "help me test this". Also triggered when the user
  wants to add tests after a merge or asks to re-run test generation.
---

# generate-test

Guided skill for scaffolding test files from a codebase exploration + user-grilled case list. Every preview requires explicit approval before the skill advances. The skill never executes tests.

## Invocation

- Slash command: `/generate-test`
- Natural-language triggers: "generate tests", "build out the test plan", "scaffold test structure", "write tests for this", "add test coverage", "create test files", "help me test this"
- Merge / re-run mode: invoked with a flag or phrase such as "re-run test generation" or "update tests after merge" — see Merge Re-run Mode below.

---

## Orchestration Loop

The skill runs six stages in order. It pauses at every preview stage and waits for an explicit approval phrase before continuing. Silence is never treated as approval.

### Stage 1 — Preflight

Before exploring the codebase, the skill checks whether it has enough context to proceed:

- Is there a target file, module, or directory in scope?
- Is there an existing test directory or convention to follow?
- Are there any existing generated test files (identified by their frontmatter)?

If essential context is missing, the skill asks clarifying questions and does not advance until they are answered.

### Stage 2 — Exploration

The skill walks the codebase to understand the source under test. Exploration is governed by `exploration-heuristics.md`, which specifies how to traverse the file tree, what patterns to look for, what to skip, and how to build a working model of the source structure.

Output of this stage: an internal map of source files, their public surface, and candidate test targets.

### Stage 3 — Structure Preview

The skill presents a proposed test-file structure: one entry per test file, showing:

- The source file it covers (`source` field)
- The proposed test file path (`test` field)
- The default agent job assigned (`unit`, `integration`, or `behavior`)

This is the **Structure preview**. The skill halts here and waits for an explicit approval phrase ("approve" or "looks good, continue") before advancing. The user may edit the proposed structure or remove entries.

### Stage 4 — Case Grill

For each approved test file, the skill runs a three-round interview to surface the cases that will populate that file. The three rounds are named and owned by `grill-topics.md`; their exact content is not duplicated here.

Round names (for reference): `Behavior`, `Integration`, `Unit`.

Every case is user-sourced. The skill does not generate cases on its own. It asks questions, proposes prompts, and records the user's answers. Cases that the user does not confirm are not written.

### Stage 5 — Cases Preview

After the grill, the skill presents the full case list per test file: every test name, its round, and a one-line description of what it asserts.

This is the **Cases preview**. The skill halts here and waits for an explicit approval phrase before writing anything. The user may add, remove, or rename cases at this stage.

### Stage 6 — Write

The skill writes each approved test file according to the schema defined in `template_test_file.md`. Every generated file includes the frontmatter fields:

- `source` — path to the source file under test
- `test` — path to this test file
- `source_sha` — SHA of the source file at generation time
- `generated_sha` — SHA of this test file at generation time

The skill never overwrites a test file that has been user-edited. Detection of user-edited files is delegated to `staleness-detection.md`.

---

## Merge Re-run Mode

When the user re-invokes the skill after a merge or branch update, the skill delegates bucket classification to `staleness-detection.md`. That file owns the bucket definitions and denylist logic; this skill does not duplicate them.

Bucket names (for reference): `Fresh`, `Stale`, `User-edited`, `Orphan`, `New`.

The skill's role in re-run mode:

1. Ask `staleness-detection.md` to classify all existing generated test files into buckets.
2. Present the classification to the user and wait for explicit approval before acting on it.
3. For `Stale` and `New` files, run the normal orchestration loop (Stages 2–6) scoped to those files only.
4. Never touch `User-edited` files. Never delete `Orphan` files without explicit user instruction.

---

## Bundled Files

The four files below are bundled with this skill. Each owns a specific domain. SKILL.md references them by name and role; their content is not duplicated here.

| File | Role |
|---|---|
| `template_test_file.md` | Defines the schema and layout for every generated test file, including required frontmatter fields and section structure. |
| `exploration-heuristics.md` | Specifies how to walk the codebase during Stage 2: traversal order, patterns to include and skip, and how to model the source surface. |
| `grill-topics.md` | Defines the three-round case grill (Behavior, Integration, Unit): the questions asked in each round and how answers are recorded as test cases. |
| `staleness-detection.md` | Owns the bucket logic for merge re-run mode: how to classify existing generated test files and what actions are permitted per bucket. |

---

## Constraints

- The skill does **not** execute tests. Test execution belongs to a future parallel-test-runner skill.
- Every case is user-sourced via the three-round grill. The skill never auto-generates cases.
- Approval is always explicit. The phrases "approve" and "looks good, continue" are the only accepted signals. Silence, ellipsis, or non-committal responses do not advance the workflow.
- The skill never overwrites user-edited test files.
- The denylist, agent-name list, and bucket list are each owned by their respective bundled file. They are not repeated here.
- This is a markdown-only skill. There are no compiled artifacts, executables, or code files.
