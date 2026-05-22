---
name: run-tests
description: >
  Orchestrate a project's existing generated test specs by dispatching one
  Explore subagent per agent block in parallel, collecting their results,
  and writing a single rolled-up result file. Use when the user says
  "run tests in parallel", "test this with parallel agents", "execute the
  generated test specs", "kick off the test agents", or otherwise asks to
  run the specs produced by the sibling `generate-test` skill.
---

# run-tests

Markdown-only orchestrator that runs the test specs produced by the sibling `generate-test` skill. The skill scans `/tests/` for spec files, asks the user for a per-agent timeout, dispatches one `Explore` subagent per `## Agent:` block in parallel, collects a trailing-YAML block from each, and writes a single rolled-up `/tests/test-result.md`.

This skill does **not** generate or edit test specs and does **not** write to source files. Spec authorship belongs to `generate-test`.

## Invocation

- Slash command: `/run-tests`
- Natural-language triggers: "run tests in parallel", "test this with parallel agents", "execute the generated test specs", "kick off the test agents", "run the specs"

---

## Orchestration Loop

### Stage 1 — Preflight

Recursively scan `/tests/` for `.md` files whose frontmatter contains all four signature fields used by `generate-test`:

- `source`
- `test`
- `source_sha`
- `generated_sha`

Files missing any of these fields are ignored.

If `/tests/` does not exist, or no matching files are found, the skill **stops** and prompts the user to run `generate-test` first. It does not dispatch any subagents in this case.

### Stage 2 — Timeout Prompt

Before dispatch, ask the user for the per-agent runtime budget (e.g. "How long should each agent run before timing out?"). This value is the timeout applied uniformly to every dispatched subagent. The skill does not proceed to dispatch until the user answers.

### Stage 3 — Parallel Dispatch

For each spec file collected in Stage 1, read its `## Agent:` blocks. Emit **one `Task` call per `## Agent:` block, all in a single message**, so every subagent runs in parallel. Each `Task` call uses:

- `subagent_type: Explore`
- The prompt and return schema defined in `agent-contract.md` (the source of truth — do not inline its body here)
- The per-agent timeout collected in Stage 2

The skill uses no `subagent_type` other than `Explore`.

### Stage 4 — Result Collection

Each subagent's final message ends with a trailing YAML block whose keys and allowed values are defined in `agent-contract.md`. Parse that block from every subagent and map it to a result record carrying `status`, `summary`, and `repro`. The `status` value is one of `pass`, `fail`, or `timeout`. The skill treats `agent-contract.md` as the authoritative definition of the schema and the enum; it does not redefine either inline.

If an agent's final message is missing or malformed, record it as `fail` with a summary explaining the parse failure.

### Stage 5 — Write

Overwrite `/tests/test-result.md` using `template_test_result.md` as the layout. The template is the source of truth for the result file's structure; this skill does not duplicate it inline.

After writing, post a single chat line in the form `X of Y passed` (verbatim), followed by a clickable markdown link to `/tests/test-result.md`.

---

## Bundled Files

| File | Role |
|---|---|
| `agent-contract.md` | The per-agent prompt and the trailing-YAML return schema (keys, enum values, formatting rules). Authoritative for what each `Explore` subagent is told and what it must return. |
| `template_test_result.md` | The layout for `/tests/test-result.md`. Authoritative for the rolled-up result file's structure. |

---

## Constraints

- The skill does **not** generate or edit test specs. Spec authorship is owned by `generate-test`.
- The skill does **not** write to source files. The only file it writes is `/tests/test-result.md`.
- All subagents are dispatched with `subagent_type: Explore`. No other subagent type is used.
- All `Task` calls for a single run are emitted in one message so the agents run in parallel.
- The YAML return schema and the `pass` / `fail` / `timeout` enum live in `agent-contract.md` and are not redefined here.
- The result-file layout lives in `template_test_result.md` and is not redefined here.
- The top-level chat summary is the verbatim string `X of Y passed`.
- This is a markdown-only skill. No compiled artifacts, executables, or code files.
