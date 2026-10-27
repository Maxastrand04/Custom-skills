# kanban

The ticket workflow. Each skill leaves an artifact the next one reads, and GitHub issues hold the board.

| Skill | What it does |
|-------|--------------|
| `map-epic` | Files an `epic: (N)` issue from a one-sentence goal and slices it into `(N.M)` tickets as sub-issues. Re-run it as tickets close to turn open questions into new tickets. |
| `new-ticket` | Files a standalone ticket for work no epic covers and sets its effort level. Owns `ticket-shapes.md`, the format every ticket follows. |
| `grill-docs` | Grills a plan, change, or idea and keeps `CONTEXT.md`, `docs/adr/`, and `docs/pcr/` up to date as decisions settle. Works with a ticket or without one, for anyone who skips the chain. |
| `architect-ticket` | The red step. Settles the public interface, writes it as stubs, writes an acceptance file of failing tests, then commits and pushes once you approve. |
| `implement-ticket` | The green step. Fills in the bodies until the acceptance file passes, without touching signatures or tests. |
| `refactor-ticket` | The refactor step. Checks the tests cover the ticket, runs the full suite, cleans the code against the project's records, folds the acceptance tests into the unit tests, and closes the issue. |
| `unit-test-ticket` | The second refactor session. Folds the acceptance file into the unit tests and tidies them. |
| `review-diff` | Reviews any branch against its ticket, fixes code smells and record breaches, and leaves a review note on the PR or the issue. For branches that skipped `refactor-ticket`. |
| `pr-ticket` | Checks what the ticket's effort level asks of the branch, then opens or rewrites its PR. |
| `execute-ticket` | Runs red, green, and refactor in one unattended session for a ticket labelled `effort:minor`, then opens a PR. |

Run `map-epic` or `new-ticket` first. The ticket's effort label then picks the route, per `new-ticket/ticket-shapes.md`:

- `effort:minor` runs `execute-ticket`.
- `effort:trivial` is an ordinary session where you watch the agent and check what no test reaches.
- `effort:medium` runs `architect-ticket` by hand, then `/kanban-ci:launch` queues the rest for kanban-ci.
- `effort:major` runs `architect-ticket`, `implement-ticket`, and `refactor-ticket` in order on one branch.

## Every branch ends at pr-ticket

However a branch was built, it gets one review before its PR:

- **`effort:major` or `effort:medium`** runs `refactor-ticket`, then `unit-test-ticket`, then `pr-ticket`.
- **`effort:minor` or `effort:trivial`**, and any branch built by hand, runs `review-diff`, then `pr-ticket`.

`pr-ticket` halts when the review its level asks for is missing. The fold commit covers major and medium. The review note covers minor and trivial. `execute-ticket` and kanban-ci still open their own PRs.
