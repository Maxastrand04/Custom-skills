---
name: autopilot-ticket
description: Runs an autopilot ticket unattended, red-green-refactor in one session, and opens a PR for review. Takes the ticket reference as its argument.
disable-model-invocation: true
---

# autopilot-ticket

One session, one ticket, all three legs of **red-green-refactor**, no gates. The ticket was labelled `autopilot` at filing because the planning would cost more than reading the finished diff, so the review moves from the contract to the PR.

**The ticket is the spec.** Expected behaviour lines are the acceptance criteria, and you turn each into a test before you write any implementation. "AC met" means those tests are green, never your own reading of the code.

---

## 1. Pin the work

Resolve the ticket from the invocation argument, meaning `42`, `#42`, or a GitHub issue URL. No argument means ask which issue, and stop until told. Never take a ticket from conversation.

`gh issue view <number> --json title,body,labels`. Read Goal, Expected behaviour, Out of scope, and Branch.

**Precondition.** The labels must carry `ticket:autopilot` or `epic:autopilot`. Otherwise halt:

> #<N> isn't an autopilot ticket. Run `/architect-ticket <N>` for the red leg, or relabel it if it qualifies under `ticket-shapes.md`.

Settle two things, and confirm both to the user in one line before touching code:

- **Branch.** `<issue-number>-<slug>`, slug from the ticket's `## Branch` section, or derived from the title when absent: 2 to 4 words, kebab-case, no articles.
- **Base.** `main`, unless the user named one at invocation or the ticket is a sub-issue of an epic that has its own branch.

Then `git checkout -b <branch>` from the base. Surface unrelated uncommitted changes before switching. Never drag them across.

## 2. Read the code

Read the region you will change, not the whole repo. Grep for the symbols the ticket's behaviour reaches, read those files, then the tests that already cover them, and every file in `docs/pcr/` and `docs/adr/` if they exist. Find the test runner command and the naming style of the test tree, since you are about to write into it.

**Point, don't paste.** Never quote the ticket or the source back into your response.

### The qualifying check

The `autopilot` label was applied at filing, before anyone read the code. Re-check it now against what you found, per the **autopilot criteria** in `../new-ticket/ticket-shapes.md`. Any one failing means the ticket was mislabelled, and this session halts with nothing committed:

> #<N> needs a decision I shouldn't make unattended: <which criterion, one line>. Relabel and run `/architect-ticket <N>`.

The same halt applies at any later step where a criterion turns out to fail. Leave a branch that already carries commits in place and name it in the halt. Never delete it.

## 3. Red

Convert each Expected behaviour line into one named test, in the project's naming style, in the file the surrounding tests live in. One behaviour per test, docstring stating the behaviour in one sentence. A `[bug]` ticket gets its standing test, the reproduction steps no longer produce the symptom.

Run them. Every one must fail because the behaviour doesn't exist yet. A test that passes asserts nothing or covers something already shipped, so sharpen it. A test that errors is broken, not red, so fix the typo or halt on a missing dependency.

A behaviour no automated test can reach is not a reason to skip it. Halt and name it. An autopilot ticket with an untestable behaviour was mislabelled.

Commit the tests:

```
Test #<N>: <ticket title>

Red.
Issue: #<N>
```

**Completion criterion:** every Expected behaviour line has one test, every test observed failing for the right reason, one commit.

## 4. Green

Implement behind the tests, one behaviour at a time. Run the tests you wrote, not the suite. Read every failure before fixing any. Track the pass number, `pass 2: 1 of 3 still red`, so a loop that isn't converging shows itself.

Commit each time a behaviour's test goes green and stays green, so the PR reads as one commit per behaviour:

```
Implement #<N>: <behaviour, in the ticket's words>

Issue: #<N>
```

Once every test you wrote is green, run the **neighbouring tests**, meaning every existing test that reaches a file you changed. Grep the test tree for each changed file's import path and exported symbols. A regression is yours to fix before moving on.

**Never edit a test to get green.** The test came from the ticket. If it looks wrong, the ticket is wrong, and that is a halt, not an edit.

**Completion criterion:** every test written in step 3 green, every neighbouring test green, one commit per behaviour.

### Loop exits

Each of these stops the session before push. Describe the failure in plain English, which test, the evidence, your best guess at the cause stated as a guess, and offer the real options: a hint from the user, relabelling to `task` and running `/architect-ticket <N>`, a `/challenge-pcr` session when a PCR is the block, or stopping here.

- **No progress.** The same test fails with the same evidence two passes running.
- **The ticket contradicts itself.** Two behaviours can't both be true.
- **A record blocks it, or a decision is needed.** A PCR or ADR the only workable implementation would breach, or a call a future reader could undo by accident. Name it. Never code around it, never edit a record, and never write one; the ticket was mislabelled, so relabel and run `/architect-ticket <N>`.

## 5. Refactor

Shape only, never behaviour. Read every changed non-test file against the whole `docs/pcr/` and `docs/adr/` sets and against `../refactor-ticket/code-standards.md`, read from that skill's directory, never searched for in the repo. A record overrides the baseline. Tests are exempt. This station writes no records and amends none; a diff that needs one is the halt above.

Re-run the tests from step 3 plus the neighbouring tests. Back to red means the edit changed behaviour, so revert it. Then commit once:

```
Refactor: <ticket title>

Issue: #<N>
```

Update `CONTEXT.md` if the branch shifted a domain term and the file exists, and `README.md` only if a contributor now needs to run or configure something new. Fold either into the refactor commit.

**Completion criterion:** every changed non-test file read against `docs/pcr/`, `docs/adr/`, and the baseline, each finding fixed, affected tests green, one commit.

## 6. Push and open the PR

```
git push -u origin <branch>
gh pr create --base <base> --title "<ticket title>" --body "$(cat ...rendered...)"
```

PR body, exactly this shape:

```
> *This was implemented by AI on autopilot. Review the diff before merging.*

Closes #<N>

## Behaviours

- <behaviour, in the ticket's words> `<test name>`
- ...

## Refactor

<one line per finding fixed, or "none">
```

Do not close the issue. `Closes #<N>` closes it on merge, and merging is the review.

## 7. Report

Close with these lines and nothing after them:

```
Branch    42-fix-expired-session
Tests     3 added green, 5 neighbouring green
Commits   5
PR        https://github.com/owner/repo/pull/57
```
