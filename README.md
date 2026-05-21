# Custom-skills

A collection of personal Claude Code skills. Each skill is a directory with a `SKILL.md` entrypoint and any bundled files it references. Skills are installed as symlinks into `~/.claude/skills/` where Claude Code picks them up automatically.

## Skills

| Skill | Description |
|-------|-------------|
| `implement-tdd` | Drive a small change test-first as Supervisor — preflight runner, write red tests, dispatch implementer, review on green |
| `implementation-planning` | Grill-me interview to stress-test a plan, then produce a structured implementation plan file |
| `new-issue` | Grill WHAT (behavior, scope, acceptance criteria) and publish a GitHub Issue |
| `project-setup` | Scaffold a fresh project end-to-end with CONTEXT.md and artifact checklist |
| `supervise-implement` | Drive an implementation plan to completion with implementer and tester subagents |

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
