# Custom-skills

A collection of personal Claude Code skills. Each skill is a directory with a `SKILL.md` entrypoint and any bundled files it references. Skills are installed as symlinks into `~/.claude/skills/` where Claude Code picks them up automatically.

## Skills

| Skill | Description |
|-------|-------------|
| `add-comments` | Grill the user into a persisted comment convention and then drive a preview-and-approve commenting loop against that convention |
| `directory-tree` | Render the current project's directory structure as a fenced markdown tree, excluding `.gitignore`'d paths |
| `generate-framework-tests` | Generate real, framework-executable tests (pytest / vitest / jest / go test / cargo test / JUnit) with a single approval gate and manifest-based drift detection; re-runs skip unchanged files via `.generate-framework-tests/sidecar-manifest.json` |
| `generate-test` | Explore the codebase, grill the user for domain cases, and write a `/tests/` directory of markdown test specs — without executing tests |
| `implement-tdd` | Drive a small change test-first as Supervisor — preflight runner, write red tests, dispatch implementer, review on green |
| `implementation-planning` | Grill-me interview to stress-test a plan, then produce a structured implementation plan file |
| `new-issue` | Grill WHAT (behavior, scope, acceptance criteria) and publish a GitHub Issue |
| `project-planning` | Run a sprint-roadmap planning session inside an existing git repo — adaptively grill to mutual understanding, propose vertical-slice sprints each with a sprint goal, then write/update CONTEXT.md and project_plan.md |
| `run-tests` | Discover and run the project's test suite, then report pass/fail results with failure details |
| `implementation-plan-execute` | Drive an implementation plan to completion in hands-on mode (model implements inline, user reviews architecture) or supervise mode (parallel implementer subagents, Architecture tester reviews architecture) |
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
