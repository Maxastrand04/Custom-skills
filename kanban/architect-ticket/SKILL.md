---
name: architect-ticket
description: Third station, the red leg of red-green-refactor. Turns a ticket into a committed branch of interface stubs and failing acceptance tests.
disable-model-invocation: true
---

# architect-ticket

You are the **red** leg of red-green-refactor, and you turn a ticket into a **red branch**: the public interface written as stubs in the real source files, the acceptance tests written against those stubs, every test failing, committed.

That commit is the whole handoff. `implement-ticket` takes it **green** and `refactor-ticket` refactors under that green. The implementer reads the issue and this diff and needs nothing else.

**The user owns the contract; the implementer owns everything behind it.** You settle the names, parameters, return values, and documented behaviour of every entry point the change adds or alters. Helpers, control flow, and data structures are the implementer's.

**The tests are the acceptance criteria.** There is no separate list. The ticket holds user-visible expected behaviour; you convert it into named test functions, and each test's name and docstring is the criterion it enforces. Never write an AC list beside the tests it duplicates.

---

## Phase 1: Grill session

You are a developer grilling a project leader about code structure. Every question in this phase runs under the `grilling` skill's interview mechanics, so invoke it. This skill supplies *what* to ask and in what order; `grilling` supplies *how*.

The phase runs as **one continuous session, ending in agreement on the contract**. Draft as you go, present work back only when something is genuinely open, and take exactly one gate on the contract, at the end.

### Resolve the ticket

This skill starts from a ticket. Resolve one of:

1. **An explicit reference** in the invocation, meaning `42`, `#42`, a GitHub issue URL, or a description of an existing issue. Resolve URLs and descriptions to the number with `gh issue list` and `gh issue view`.
2. **A ticket published in this session** by `new-ticket` or `map-epic`. Confirm with the user before adopting it; never route silently.
3. **Neither.** Ask which issue this is, and point at `/new-ticket` if none exists. Do not architect from a conversation.

Then read the body in full with `gh issue view <ref> --json title,body,labels`. Take **Goal**, **Expected behaviour**, and **Out of scope** as given. They are the user-visible WHAT and were settled when the ticket was filed. Everything you grill sits below them.

Capture the **branch slug** from the ticket's `## Branch` section. The branch is `<issue-number>-<slug>`. The ticket chose the slug; you supply the number. Older tickets with no `## Branch` section fall back to `<issue-number>-<short slug from the title>`.

### Exploration, runs before any question

Ground the grill in what exists:

1. **Project-level reads**, where present: `CONTEXT.md`, top-level `README.md`, the project root listing, and every file in `docs/adr/`. The ADRs are binding decisions about the shape the codebase takes, so the interface you propose has to sit inside them.
2. **Change-specific reads.** Grep and read the modules the change will touch, their neighbours, and the **existing public interface** the new one sits beside: signatures, naming, error types, module layout.
3. **The test tree.** Find where tests live, how they are named, what fixtures and factories exist, and the runner command. You are about to write tests here, so their shape has to match.

Emit a short **"What I found"** summary covering the relevant modules, the conventions in the affected area, the interface the change plugs into, and the runner command. **Wait for the user to correct misreads.**

### The public interface

**The hardest-grilled part of the session.** For every entry point the change adds or alters, drive four things to a settled answer:

1. **Name.** The exact identifier, in the naming style Exploration found.
2. **Parameters.** Each one's name, type, whether it's required, and its default.
3. **Return value.** Its type, and what it *means* to the caller.
4. **Contract.** What the caller may rely on: errors raised and when, edge-case behaviour, invariants, side effects.

Rules for this block:

- **Nothing is settled while any of the four is open.** A parameter with no type, a return described only as "the result", an error path nobody named. Each is an unresolved branch. Keep going.
- **Grill the interface, not the implementation.** "One function or a class with three methods?" is the contract, so grill it. "A dict or an LRU cache for the tokens?" sits behind the boundary, so don't spend the user's attention on it.
- **Cover every expected behaviour in the ticket.** Each one has to be reachable through something on this list. A behaviour no signature can reach means the contract is incomplete, so surface the gap and resolve it.
- **Stay inside `docs/adr/`.** If the natural interface would breach a recorded decision, that is not yours to override. Name the ADR and take it to the user, who either accepts a different interface or stops to run `/challenge-adr` as its own session. Do not design against a decision you expect to fall.

Draft from Exploration first. Propose the interface that fits what already exists and let the user correct it, rather than asking from a blank page.

### The acceptance tests

Now convert the ticket's expected behaviour into named tests. This is where the ticket's coarse WHAT becomes the exact bar the implementer has to clear, and it is yours to set.

For each behaviour in the ticket, settle:

- **The test function name**, in the project's naming style, and the **file** it lands in.
- **What it asserts**, in one sentence, phrased as an observable outcome through the public interface.

Then sweep for what the ticket didn't say, because a ticket carries user-visible behaviour and stops there:

- **Edge cases and failure modes** the contract names. Every error in a docstring earns a test.
- **Boundaries**: empty, missing, zero, duplicate, and conflicting inputs.
- **Behaviour this change must not break**, wherever it extends something that already ships.

**One behaviour per test.** A test asserting three things fails ambiguously, and the implementer reads a failure as an instruction. Split it.

**State plainly to the user any behaviour no automated test can reach.** It is a manual check, not a test. Don't fake one.

### Confirmation gate

Present the complete draft **once**: the public interface as fenced stubs grouped by file, the test list as name plus file plus one-line assertion, the branch name, and any manual checks. Add 1-2 sentences of reasoning where a choice was close. **Wait for the user to confirm or correct the whole thing**, and iterate until they agree it is the full contract for "done".

If drafting the tests surfaces a gap in the interface, fix it inline before presenting. This is one draft, not two.

Only **after the draft is confirmed**, say:

> "Contract settled. Writing the red branch now."

Then proceed immediately to Phase 2 without waiting to be prompted.

---

## Phase 2: Write the red branch

### 1. Branch

`git checkout -b <issue-number>-<slug>`, or `git checkout` it if it already exists. If the working tree carries unrelated uncommitted changes, surface that before switching rather than dragging them across.

### 2. Stubs into the source files

Write each settled entry point into its real file: the signature, the contract as the docstring, and a body that raises the language's not-implemented error. Real source files, in the project's language and style, not pseudocode and not a scratch file.

- **Match the file's existing shape.** Imports, ordering, and export style follow what is already there.
- **Create a file only when the interface genuinely needs a new one.** Prefer the module the surrounding interface already lives in.
- **Write nothing behind the boundary.** No helpers, no control flow, no data structures. Every one of those is the implementer's call.

### 3. Tests

Write every confirmed test, calling the code **only through the stubs as written**. These tests are what pin the contract, so a test that reaches around the public interface into internals pins nothing and blocks the implementer from restructuring.

Each test's docstring states the behaviour it enforces, in one sentence.

### 4. Go red

Run the tests. Read the output. Every one must **fail because the behaviour doesn't exist yet**.

Two ways this goes wrong, and both mean you are not done:

- **A test passes.** It asserts nothing real, or the behaviour already ships. Sharpen it, or take it to the user if the ticket asked for something already built.
- **A test errors** on a typo, a bad import, a missing fixture, or a missing module. That is broken, not red. A missing module or fixture is the interesting case: the change stands on something that isn't there. Fix a typo yourself, but **halt on a genuinely absent dependency** and take it to the user, because building it is separate work and is theirs to schedule.

What the test run can't reach is external: a credential, a running service, a created bucket or queue. Name those to the user in one line if the contract needs any.

**Completion criterion:** every test named in the confirmed draft exists, has been run, and has been observed failing for the right reason. Not "should fail". Observed.

### 5. ADR, only when a decision was weighed

Write an ADR when this session **weighed options and made a hard-to-reverse call**: a boundary between modules, a dependency direction, a data ownership decision, an interface shape chosen over a real alternative.

The test is whether a future reader could undo it by accident. If they'd look at the code, see no reason for the shape, and "simplify" it, the reason has to be on record.

Follow [`../codebase-rules/ADR-FORMAT.md`](../codebase-rules/ADR-FORMAT.md) exactly, take the next free number, and confirm the Decision line with the user before writing the file. Most tickets produce no ADR, and that's correct.

**Never modify an existing ADR here.** Changing one takes a full `/challenge-adr` session and cannot be done as part of this one.

### 6. Commit

Stage the stubs, the tests, and any ADR, and commit on the branch.

```
Architect #<N>: <ticket title>

Interface and acceptance tests. Red.
Issue: #<N>
```

Don't push unless the user asks.

### 7. Report

Four lines:

```
Branch    42-oauth-admin-login
Stubs     src/auth/oauth.py, src/auth/session.py
Tests     6 written, 6 red
Commit    a1b2c3d
```

Then say that `/implement-ticket` takes it green, and name any manual checks or external resources the user still owns.
