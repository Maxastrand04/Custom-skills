# Archived skills

Skills I've stopped using. Kept because the thinking in them is still worth raiding, not because I intend to run them.

`install.sh` skips this directory — it walks a fixed list of live categories (`kanban`, `developer-tools`, `schoolwork`) and `archive` isn't on it. Nothing in here is symlinked into `~/.claude/skills/`.

| Skill | Why it's here |
|-------|---------------|
| `generate-test` | Wrote markdown test *specs* under `tests/` rather than runnable code. Superseded by `generate-framework-tests`, which produces real pytest / vitest / jest / go test / cargo test / JUnit files. |
| `run-tests` | Only existed to execute `generate-test`'s markdown specs via parallel `Explore` agents. Dead once the specs stopped being generated — real framework tests run with the project's own runner. |
| `directory-tree` | Standalone tree renderer. `project-planning` used to invoke it to fill the Directory tree section of `project_plan.md`; that section now falls back to its placeholder. |

To bring one back: move it into a live category and re-run `./install.sh <name>`.
