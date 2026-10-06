# kanban

The ticket workflow. Each skill leaves an artifact the next one reads, and GitHub issues hold the board.

| Skill | What it does |
|-------|--------------|
| `map-epic` | Files an `(N) [epic]` issue from a one-sentence goal and slices it into `(N.M)` tickets as sub-issues. Re-run it as tickets close to turn open questions into new tickets. |
| `new-ticket` | Files a standalone ticket for work no epic covers. Owns `ticket-shapes.md`, the format every ticket follows. |
| `architect-ticket` | The red step. Settles the public interface, writes it as stubs, writes an acceptance file of failing tests, and commits. |
| `implement-ticket` | The green step. Fills in the bodies until the acceptance file passes, without touching signatures or tests. |
| `refactor-ticket` | The refactor step. Checks the tests cover the ticket, runs the full suite, cleans the code against the project's records, folds the acceptance tests into the unit tests, and closes the issue. |
| `autopilot-ticket` | Runs red, green, and refactor in one session for a ticket labelled `autopilot`, then opens a PR. |

Run `map-epic` or `new-ticket` first, then `architect-ticket`, `implement-ticket`, and `refactor-ticket` in order on one branch.
