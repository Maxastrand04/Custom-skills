# kanban

The workflow skills. They run in order and each one leaves an artifact the next one reads, so nothing is re-derived from memory.

There is no plan file. GitHub holds project state: an epic is its `(N) [epic]` issue, a task is a sub-issue of one, and done means closed.

The epic issues the board starts from come from `../developer-tools/project-planning`, which runs once per project rather than once per unit of work, so it isn't a station.

## The stations

### `map-epic`

Once per epic. Slices one epic goal into `(N.M)` tickets, filed as native sub-issues of the epic and wired with native blocking, then fills in the epic issue's notes, decisions, and fog. Research and prototype tickets are first-class here, so unknowns get charted instead of guessed at.

### `architect-ticket`

Once per ticket, and the **red** leg. Grills hardest on the public interface, meaning the names, parameters, return values, and contracts the implementer is held to. Writes that interface as stubs into the real source files, writes the ticket's tests into one **acceptance file** against them, runs it, confirms every test fails, writes an ADR for each argument the grill had, and commits.

### `implement-ticket`

The **green** leg. Reads the ticket for the why and `git diff main...HEAD` for the what, then fills in the bodies until the acceptance file passes. It runs nothing else, because the rest of the suite may carry requirements this ticket overwrote. Signatures and tests are frozen; everything behind them is free. A contract that proves wrong mid-run halts for a real decision rather than being edited quietly.

### `refactor-ticket`

The **refactor** leg, and the last station. First it gates the diff true-to-spec, asking whether the acceptance file genuinely covers the ticket's expected behaviour and whether the code meets it. Then it runs the whole suite and reconciles it: an old test the ticket contradicts is stale and gets rewritten to the new requirement, a red test nothing contradicts is a regression and gets fixed in its own commit or halted on. Under that full green it edits the code into line with the PCRs in `docs/pcr/`, the ADRs in `docs/adr/`, and its own `code-standards.md` baseline and commits the refactor separately. Last it folds the acceptance file's tests into the module test files, deletes it, and closes the issue.

### `autopilot-ticket`

The three legs in one unattended session, for a ticket labelled `autopilot` at filing. The label means settling the contract up front would cost more than reading the finished diff, which is true of small refactors, bug fixes, and implementation swaps behind a stable interface. The criteria live in `new-ticket/ticket-shapes.md`, and the station re-checks them against the code before writing anything. It writes the tests from Expected behaviour, takes them green one commit per behaviour, refactors under the same records and baseline as `refactor-ticket`, pushes, and opens a PR that closes the issue on merge. The review that `architect-ticket` does before the code moves to the PR after it.

### `new-ticket`

Sits beside the chain rather than on it. Files a standalone ticket for work no epic covers, and owns `new-ticket/ticket-shapes.md`, the single source of truth for every ticket body, title, label, and `gh` publish call. `map-epic` reads that same file, which is why an epic ticket and a standalone ticket look identical.

## TDD, red-green-refactor

The last three stations are one TDD cycle on one ticket and one branch, split across three sessions instead of three phases of one. Each name says which leg it is.

**Red.** `architect-ticket` leaves the branch red: stubs in the real source files, one acceptance file written against them, every test in it observed failing, committed. That commit is the entire handoff. A signature in a source file and a failing test carry the contract exactly where a plan file could only describe it, which is why there is no plan file.

**Green.** `implement-ticket` reads the ticket and the diff and fills in the bodies until the acceptance file passes. It needs nothing else, because the red branch already says what must become true. A test that *errors* rather than fails is how a missing dependency surfaces, which is what a prerequisites checklist used to be for.

**Refactor.** `refactor-ticket` changes shape and never behaviour. The green suite is what buys that, and it is the handoff from the second leg to the third. A test going red means the edit changed behaviour and was therefore never a refactor, so it gets reverted rather than accommodated.

Two things stay frozen from the moment the architect commits them, the signatures and the acceptance file, which is what keeps the three legs one cycle rather than three people editing the same branch. The one exception is `refactor-ticket`'s true-to-spec gate, where a test that does not honestly cover the ticket can be fixed with my go-ahead. Green only means the tests pass, not that they were the right tests, and refactoring code that is wrong spec-wise is wasted work.

## The acceptance file is disposable

Acceptance criteria describe a ticket, and a ticket is a moment. Left in the suite as written, every closed ticket's criteria stay frozen and each new ticket has to satisfy requirements that may no longer hold, which is friction nobody asked for. So the acceptance file lives only on the ticket branch. `refactor-ticket` folds its tests into the module test files, where they are ordinary unit tests any later ticket may rewrite, then deletes it. Main never carries an acceptance file, and the durable safety net is the unit suite, which the newest ticket always wins against.

Run them in order. Each one halts on its own precondition otherwise.

`autopilot-ticket` is the same cycle without the two handoffs, so the two frozen things are never reviewed before the PR. That is what the `autopilot` label trades, and why it only goes on a ticket where nothing outside its own files would notice a wrong call.

## Records accumulate as the board runs

Two kinds, one format, `architect-ticket/RECORD-FORMAT.md`. An ADR binds one region of the code: a module's purpose and shape, what code inside it may not do, a dependency direction, an interface that beat a real alternative. A PCR binds the whole project: stack, allowed libraries, naming, comment convention, OOP or not, test suite.

Only the stations that argue write. `architect-ticket` writes an ADR per argument its grill had, which is one or two on a ticket that argued something and none on most. `refactor-ticket` writes one when a diff introduces a shape neighbours will copy. `implement-ticket` and `autopilot-ticket` write none, because neither makes a decision; one of them weighing a call is a contract gap and halts. Either writing station may amend an ADR when the work gives it a reason, with the reason in the session and the commit message and never in the file. A PCR moves only in a `/challenge-pcr` session, because changing one ripples through every file. `project-planning` seeds the PCRs, and `architect-ticket` adds one when its ticket is the first to settle something project-wide.

There is no separate skill that surveys a codebase for records. They come from tickets.

## Conventions

**Tickets hold user-visible behaviour, never codebase detail.** The exact bar lives in the tests `architect-ticket` writes, which is the one station that has read the code and settled the interface.

**Every skill here is user-invoked**, via `disable-model-invocation: true`, as is everything outside `../behaviour/`. The chain hands off through artifacts, not by one skill calling the next, so none of them needs a model-facing description and none pays context load. Starting a station is my call about what happens next.

Otherwise a skill belongs here only if it's a link in that chain. Anything that helps while coding but isn't a station on the board lives in `../developer-tools/`.
