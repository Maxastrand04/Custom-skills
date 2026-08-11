# agent-contract

Canonical contract for every `Explore` subagent dispatched by the `run-tests` skill. Defines the prompt fields each agent receives and the trailing-YAML schema each agent must return. SKILL.md references this file as the single source of truth — do not duplicate this schema elsewhere.

---

## Prompt template

Each dispatched agent receives a self-contained prompt with the following fields. Every field is required.

- **Job** — the agent block's job label, one of `unit`, `integration`, or `behavior`. Tells the agent what kind of verification to perform.
- **Targets** — the list of source paths, modules, or surfaces under test, copied verbatim from the spec's agent block.
- **Cases** — the ordered list of cases to verify, copied verbatim from the spec's agent block. The agent must verify every case; partial verification counts as `fail`.
- **Timeout budget** — the per-agent runtime budget (e.g. `5m`, `120s`) supplied by the user at skill invocation. See the timeout contract below.
- **Working directory** — the absolute path the agent should treat as the project root for all Bash and Read operations.

The prompt also restates the return schema and the capability constraints below so the agent is fully briefed without needing to read this file.

---

## Timeout contract

The agent self-polices its runtime against the supplied timeout budget.

- The agent tracks elapsed time from prompt start.
- If the budget is exceeded **before** all cases are verified, the agent stops work immediately and returns the trailing-YAML block with `status: timeout`.
- The agent does **not** continue past the budget hoping to finish. Partial progress past the deadline is discarded.
- The orchestrator does not enforce timeouts externally — the contract is honour-based and lives inside the agent.

---

## Capabilities

Each agent has **read + execute** access only.

- **Allowed:** `Read`, `Bash`, `Grep`, `Glob`, and any read-only inspection tools needed to run tests and observe results.
- **Forbidden:** `Edit`, `Write`, `NotebookEdit`, or any other tool that modifies files on disk. The agent must **not** edit, write, create, or delete source files, test files, or any project artifact. Test execution is read+run only.

If a case cannot be verified without modifying source, the agent reports `fail` with a `summary` explaining the blocker — it does not attempt the modification.

---

## Return schema

The agent's final message must end with a fenced YAML block containing **exactly** these three keys — no extras, no renames:

- **status** — one of exactly `pass`, `fail`, `timeout`. No other values are permitted.
- **summary** — plain English, one line. **Required** when `status` is `fail` or `timeout`. Omit (or leave empty) when `status` is `pass`.
- **repro** — ordered list of shell-or-action steps that reproduce the failure locally. **Required** when `status` is `fail` or `timeout`. Omit (or leave empty) when `status` is `pass`.

### Status enum

| Value | Meaning |
|---|---|
| `pass` | Every case in the agent block verified successfully within the timeout budget. |
| `fail` | One or more cases did not verify, or verification produced an unexpected result. |
| `timeout` | Timeout budget exceeded before all cases could be verified. |

### Field formats

- `summary` — a single line of plain English describing the failure cause. Not a stack trace, not a code dump. Example: `"login endpoint returned 500 instead of 401 for invalid credentials"`.
- `repro` — an ordered YAML list. Each entry is one shell command or one user-visible action. Steps should run top-to-bottom from the supplied working directory and end at the observed failure.

---

## Examples

Pass case — minimal block:

```yaml
status: pass
summary:
repro:
```

Fail case — full block:

```yaml
status: fail
summary: login endpoint returned 500 instead of 401 for invalid credentials
repro:
  - cd /Users/max/GitHub/example-project
  - npm install
  - npm run dev
  - curl -X POST http://localhost:3000/login -d '{"user":"x","pass":"wrong"}'
  - observe response code is 500 (expected 401)
```

Timeout case:

```yaml
status: timeout
summary: integration suite exceeded 5m budget while running case 3 of 7
repro:
  - cd /Users/max/GitHub/example-project
  - npm test -- --grep "checkout flow"
  - wait — suite hangs on database fixture seed
```
