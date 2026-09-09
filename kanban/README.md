# kanban

The workflow skills. They run in order and each one leaves an artifact the next one reads, so nothing is re-derived from memory.

There is no plan file. GitHub holds project state: an epic is its `(N) [epic]` issue, a task is a sub-issue of one, and done means closed.

The epic issues the board starts from come from `../developer-tools/project-planning`, which runs once per project rather than once per unit of work, so it isn't a station.

## The stations

### `map-epic`

Once per epic. Slices one epic goal into `(N.M)` tickets, filed as native sub-issues of the epic and wired with native blocking, then fills in the epic issue's notes, decisions, and fog. Research and prototype tickets are first-class here, so unknowns get charted instead of guessed at.

### `architect-ticket`

Once per ticket, and the **red** leg. Grills hardest on the public interface, meaning the names, parameters, return values, and contracts the implementer is held to. Writes that interface as stubs into the real source files, writes the acceptance tests against them, runs them, confirms every one fails, and commits.

### `implement-ticket`

The **green** leg. Reads the ticket for the why and `git diff main...HEAD` for the what, then fills in the bodies until every acceptance test passes. Signatures and tests are frozen; everything behind them is free. A contract that proves wrong mid-run halts for a real decision rather than being edited quietly. On green it closes the issue.

### `refactor-ticket`

The **refactor** leg, and the last station. First it gates the diff true-to-spec, asking whether the acceptance tests genuinely cover the ticket's expected behaviour and whether the code meets it. Then it edits the code into line with the ADRs in `docs/adr/` and its own `code-standards.md` baseline, re-runs the affected tests, and commits the refactor separately from the implementer's work.

### `new-ticket`

Sits beside the chain rather than on it. Files a standalone ticket for work no epic covers, and owns `new-ticket/ticket-shapes.md`, the single source of truth for every ticket body, title, label, and `gh` publish call. `map-epic` reads that same file, which is why an epic ticket and a standalone ticket look identical.

## TDD, red-green-refactor

The last three stations are one TDD cycle on one ticket and one branch, split across three sessions instead of three phases of one. Each name says which leg it is.

**Red.** `architect-ticket` leaves the branch red: stubs in the real source files, acceptance tests written against them, every one observed failing, committed. That commit is the entire handoff. A signature in a source file and a failing test carry the contract exactly where a plan file could only describe it, which is why there is no plan file.

**Green.** `implement-ticket` reads the ticket and the diff and fills in the bodies until the suite passes. It needs nothing else, because the red branch already says what must become true. A test that *errors* rather than fails is how a missing dependency surfaces, which is what a prerequisites checklist used to be for.

**Refactor.** `refactor-ticket` changes shape and never behaviour. The green suite is what buys that, and it is the handoff from the second leg to the third. An affected test going red means the edit changed behaviour and was therefore never a refactor, so it gets reverted rather than accommodated.

Two things stay frozen from the moment the architect commits them, the signatures and the tests, which is what keeps the three legs one cycle rather than three people editing the same branch. The one exception is `refactor-ticket`'s true-to-spec gate, where a test that does not honestly cover the ticket can be fixed with my go-ahead. Green only means the tests pass, not that they were the right tests, and refactoring code that is wrong spec-wise is wasted work.

Run them in order. Each one halts on its own precondition otherwise.

## Conventions

**Tickets hold user-visible behaviour, never codebase detail.** The exact bar lives in the tests `architect-ticket` writes, which is the one station that has read the code and settled the interface.

**Every skill here is user-invoked**, via `disable-model-invocation: true`, as is everything outside `../behaviour/`. The chain hands off through artifacts, not by one skill calling the next, so none of them needs a model-facing description and none pays context load. Starting a station is my call about what happens next.

Otherwise a skill belongs here only if it's a link in that chain. Anything that helps while coding but isn't a station on the board lives in `../developer-tools/`.
