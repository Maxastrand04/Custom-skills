# Archived skills

Skills I've stopped using. Kept because the thinking in them is still worth raiding, not because I intend to run them.

`install.sh` skips this directory. It walks a fixed list of live categories (`kanban`, `developer-tools`, `behaviour`, `schoolwork`) and `archive` isn't on it. Nothing in here is symlinked into `~/.claude/skills/`.

| Skill | Why it's here |
|-------|---------------|
| `generate-test` | Wrote markdown test *specs* under `tests/` rather than runnable code. Superseded by `generate-framework-tests`, which produces real pytest / vitest / jest / go test / cargo test / JUnit files. |
| `run-tests` | Only existed to execute `generate-test`'s markdown specs via parallel `Explore` agents. Dead once the specs stopped being generated, since real framework tests run with the project's own runner. |
| `implementation-planning` | Wrote a plan file to `implementation_plans/` describing an interface in prose, then handed it to a fresh session. Superseded by `architect-ticket`, which writes the interface into the source files and the acceptance tests into the test tree, so the handoff is a red branch instead of a document. |
| `implementation-plan-execute` | Drove that plan file through a Phase 0 / Red / Green / Verification loop. Superseded by `implement-ticket`, which reads the ticket and the architect's committed diff and only has to take it green. The phase scaffolding went with the plan file. |
| `implement-tdd` | The small-change bypass around the board: runner preflight, red tests written by a Supervisor, one `claude` implementer dispatched per attempt, an `Explore` reviewer on green. Superseded by `architect-ticket`, `implement-ticket` and `refactor-ticket`, which run the same red-green-refactor cycle across three sessions, with a real ticket behind it and no subagent dispatch. |
| `directory-tree` | Standalone tree renderer. `project-planning` used to invoke it to fill a Directory tree section of `project_plan.md`; both the plan file and that section are gone. |

To bring one back: move it into a live category and re-run `./install.sh <name>`.
