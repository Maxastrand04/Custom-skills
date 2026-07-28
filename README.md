# Custom-skills

A collection of personal Claude Code skills. Each skill is a directory with a `SKILL.md` entrypoint and any bundled files it references. Skills are installed as symlinks into `~/.claude/skills/` where Claude Code picks them up automatically.

## Skills

| Skill | Description |
|-------|-------------|
| `add-comments` | Grill the user into a persisted comment convention and then drive a preview-and-approve commenting loop against that convention |
| `codebase-rules` | Codify a project's architecture/coding rules as enforceable one-rule-per-ADR files in `docs/adr/` — the pillar a reviewer cites and an implementer stays within; surveys the codebase, grills each rule, writes `Rule / Why / How-to-check` |
| `directory-tree` | Render the current project's directory structure as a fenced markdown tree, excluding `.gitignore`'d paths |
| `generate-framework-tests` | Generate real, framework-executable tests (pytest / vitest / jest / go test / cargo test / JUnit) with a single approval gate and manifest-based drift detection; re-runs skip unchanged files via `.generate-framework-tests/sidecar-manifest.json` |
| `generate-test` | Explore the codebase, grill the user for domain cases, and write a `/tests/` directory of markdown test specs — without executing tests |
| `grilling` | Grill the user relentlessly about a plan or design, one question at a time down each branch of the decision tree, until shared understanding |
| `implement-tdd` | Drive a small change test-first as Supervisor — preflight runner, write red tests, dispatch implementer, review on green |
| `implementation-planning` | Grill-me interview to stress-test a plan, then produce a structured implementation plan file |
| `new-issue` | Grill WHAT (behavior, scope, acceptance criteria) and publish a GitHub Issue; supports plan-driven invocation (`N.M`) to seed from `project_plan.md`, file as a sub-issue under the sprint parent, and write the issue number back to the plan |
| `project-planning` | Run a sprint-roadmap planning session inside an existing git repo — adaptively grill to mutual understanding, propose vertical-slice sprints each with a sprint goal, then write/update CONTEXT.md and project_plan.md |
| `run-tests` | Discover and run the project's test suite, then report pass/fail results with failure details |
| `implementation-plan-execute` | Drive an implementation plan to completion — model implements each Group inline with freedom within the project's rule-ADRs; the final Verification phase runs the acceptance tests once, then commits; architecture is left to a separate code-review session |
| `review-edits` | Reviewer at the end of the work — review the committed diff along two parallel axes: Standards (conforms to the rule-ADRs in `docs/adr/`, plus a Fowler code-smell baseline) and Spec (faithful to the originating acceptance criteria, no scope creep). Handles both a plan-backed `implementation-plan-execute` run (Verification already settled does-it-work, this judges is-it-right) and a small issue done inline with no plan (derives the issue from the branch's number, and checks the ACs itself) |
| `sprint-planning` | Take one sprint from `project_plan.md`, slice its goal into caveman-style `(N.M)` tasks, and create the sprint's parent `(N)` GitHub issue — middle link of the chain: `project-planning` → `sprint-planning` → `new-issue` |

## Installation

Clone the repo and run the installer:

```bash
git clone <repo-url> ~/GitHub/Custom-skills
cd ~/GitHub/Custom-skills
./install.sh
```

This symlinks every skill into `~/.claude/skills/`. To install a specific skill:

```bash
./install.sh implement-tdd
```

### Requirements

- Claude Code CLI installed
- `~/.claude/skills/` is the standard skills directory — the installer creates it if missing

### Updating

Pull the latest changes. Because installs are symlinks, Claude Code picks up updates automatically — no re-install needed.

```bash
git pull
```
