# kanban

The ticket workflow. Each skill leaves an artifact the next one reads, and GitHub issues hold the board.

| Skill | What it does |
|-------|--------------|
| `map-epic` | Files an `epic: (N)` issue from a one-sentence goal and slices it into `(N.M)` tickets as sub-issues. Re-run it as tickets close to turn open questions into new tickets. |
| `new-ticket` | Files a standalone ticket for work no epic covers and sets its effort level. Owns `ticket-shapes.md`, the format every ticket follows. |
| `grill-docs` | Interviews you about a plan one round at a time, with a recommended answer for each question, and keeps `CONTEXT.md`, `docs/adr/`, and `docs/pcr/` up to date as decisions settle. Claude can start it on its own, and `new-ticket`, `map-epic`, `architect-ticket`, and `brainstorming` borrow it for their interviews. Works with a ticket or without one. |
| `architect-ticket` | The red step. Settles the public interface, writes it as stubs, writes an acceptance file of failing tests, then commits and pushes once you approve. |
| `implement-ticket` | The green step. Fills in the bodies until the acceptance file passes, without touching signatures or tests. |
| `refactor-ticket` | The refactor step. Checks the tests cover the ticket, runs the full suite, cleans the code against the project's records, folds the acceptance tests into the unit tests, and closes the issue. |
| `unit-test-ticket` | The second refactor session. Folds the acceptance file into the unit tests and tidies them. |
| `review-diff` | Reviews any branch against its ticket, fixes code smells and record breaches, and leaves a review note on the PR or the issue. For branches that skipped `refactor-ticket`. |
| `pr-ticket` | Checks the branch is committed and green, then rewrites its ticket PR from the commits and diff. It marks the PR ready only when `For the reviewer` has no red or yellow items, and otherwise leaves it a draft for you to flip. Runs in a fresh subagent, and Claude starts it on its own whenever a ticket branch needs its PR. Works without the kanban. |
| `execute-ticket` | Runs red, green, and refactor in one unattended session for a ticket labelled `effort:minor`, then hands the branch to `pr-ticket`. |
| `tdd-ticket` | The orchestrator. Runs a `medium`, `major` or `minor` ticket's whole route from one session: the architect grill with you, then each later station in a fresh subagent that loads its own model-invoked skill, then `pr-ticket`. It never copies station instructions into subagent prompts. Escalates Spec, interface and record changes to you. Claude Code only, and not in the plugin. |
| `helper-skill` | Carries copies of the base files the stations read, so the kanban works when the base ships as a separate plugin. Nobody runs it. Edit the originals and run `scripts/sync-helper-skill.py`. |
| `amend-pcr` | Loads when a convention in `docs/pcr/` blocks the work. Ranks the ripple, gives a verdict, and amends or retires the PCR only after you approve the listed changes. The only skill that edits `docs/pcr/`. Model-invoked. |

Run `map-epic` or `new-ticket` first. They label each ticket with how much of you it needs, per `new-ticket/ticket-shapes.md`. The label then picks the route:

- `effort:medium`, `effort:major` and `effort:minor` run `tdd-ticket`. It grills the interface with you on `medium` and `major`, then runs every later station in a fresh subagent and asks you only what it may not decide. On `minor` it runs `execute-ticket` and `review-diff` with no grill. You next see the PR.
- `effort:trivial` is an ordinary session where you watch the agent and check what no test reaches.

The six stations `architect-ticket`, `implement-ticket`, `refactor-ticket`, `unit-test-ticket`, `execute-ticket` and `review-diff` are model-invoked so subagents can load them through the Skill tool. `tdd-ticket` remains user-invoked. You can still run the stations by hand, in the order `tdd-ticket` would.

## Every branch has a ticket PR

Whichever station creates a ticket's branch opens a draft PR for it straight away, and every later station writes its notes there. The ticket keeps the spec, and the PR keeps the history. `review-diff` opens the draft on branches built in an ordinary session. Spec changes go on both as dated amendment notes, once you approve them. The contract is `pr-ticket/ticket-pr.md`, which the stations read through `helper-skill`.

## Every branch ends at pr-ticket

However a branch was built, it gets one review before its PR:

- **`effort:major` or `effort:medium`** runs `refactor-ticket`, then `unit-test-ticket`, then `pr-ticket`.
- **`effort:minor` or `effort:trivial`**, and any branch built by hand, runs `review-diff`, then `pr-ticket`.

Nothing enforces the review on a hand-run route. `pr-ticket` says in the PR body whether a review note covers the branch, and flags test files left off the project's convention, such as an unfolded acceptance file. `execute-ticket` calls `pr-ticket` itself, except under `tdd-ticket`, which runs both reviews and `pr-ticket` for you.
