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
| `codebase-rules` | Surveyed a codebase and grilled its de-facto conventions into ADRs in one session. Superseded by the board itself: `architect-ticket` writes an ADR per argument its grill had and `refactor-ticket` writes one when a diff introduces a shape neighbours will copy, so records accumulate ticket by ticket. Project-wide conventions became PCRs, seeded by `project-planning`. The one thing lost is the bootstrap: an existing codebase's conventions only get a record once a ticket touches them. `ADR-FORMAT.md` moved to `kanban/architect-ticket/RECORD-FORMAT.md`. |
| `add-comments` | Grilled a `comment-convention.md` into the repo, then walked the code symbol by symbol. Retired because the comment convention is now a PCR in `docs/pcr/`, and no skill writes a separate rules document into a repo. The preview-walk went with it; bringing it back means having it read the PCR instead of its own file. |
| `directory-tree` | Standalone tree renderer. `project-planning` used to invoke it to fill a Directory tree section of `project_plan.md`; both the plan file and that section are gone. |

To bring one back: move it into a live category and re-run `./install.sh <name>`.
