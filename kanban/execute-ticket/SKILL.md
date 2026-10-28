---
name: execute-ticket
description: Executes an effort:minor ticket unattended, red-green-refactor in one session, and opens a PR for review. Takes the ticket reference as its argument.
disable-model-invocation: true
---

# execute-ticket

One session, one ticket, all three legs of **red-green-refactor**, no gates. The ticket was labelled `effort:minor` at filing because the planning would cost more than reading the finished diff, so the review moves from the contract to the PR.

**The ticket is the spec.** Its Behaviour lines are the acceptance criteria, and you cover each with a test before you write any implementation. "AC met" means those tests are green, never your own reading of the code.

---

## 1. Pin the work

Resolve the ticket from the invocation argument, meaning `42`, `#42`, or a GitHub issue URL. No argument means ask which issue, and stop until told. Never take a ticket from conversation.

`gh issue view <number> --json title,body,labels,comments`. Read Goal, Spec, Out of scope, and Branch, read as the current Spec per `../pr-ticket/ticket-pr.md`. Spec's Interface lines tell you which pieces to build, and you name them in the project's style.

**Precondition.** The labels must carry `effort:minor`. Otherwise halt:

> #<N> isn't an `effort:minor` ticket. Take the route its effort level names in `ticket-shapes.md`, or relabel it if it qualifies.

Settle two things, and confirm both to the user in one line before touching code:

- **Branch.** `<issue-number>-<slug>`, slug from the ticket's `## Branch` section, or derived from the title when absent: 2 to 4 words, kebab-case, no articles.
- **Base.** `main`, unless the user named one at invocation.

Then `git checkout -b <branch>` from the base. Surface unrelated uncommitted changes before switching. Never drag them across. Open the branch's **ticket PR** per `../pr-ticket/ticket-pr.md` straight away.

Every halt below also goes on the ticket PR, word for word, with `gh pr comment <PR>`, so the history survives the session.

## 2. Read the code

Read the region you will change, not the whole repo. Grep for the symbols the ticket's behaviour reaches, read those files, then the tests that already cover them, and every file in `docs/pcr/` and `docs/adr/` if they exist. Find the test runner command and the naming style of the test tree, since you are about to write into it.

**Point, don't paste.** Never quote the ticket or the source back into your response.

### The qualifying check

The `effort:minor` label was applied at filing, before anyone read the code. Re-check it now against what you found, per the **effort criteria** in `../new-ticket/ticket-shapes.md`. Any of the three checks failing, or a Behaviour line no automated test reaches, means the ticket was mislabelled, and this session halts with nothing committed beyond the start commit:

> #<N> needs a decision I shouldn't make unattended: <which check, one line>. Relabel it to the effort level that check gives and take that route.

The same halt applies at any later step where a check turns out to fail. Leave a branch that already carries commits in place and name it in the halt. Never delete it.

## 3. Red

Cover every Behaviour line with at least one named test, in the project's naming style, in the file the surrounding tests live in. A flow step that only sets up the next one is covered by that next step's test. Interface lines get no tests. One behaviour per test, docstring stating the behaviour in one sentence. A `fix` ticket gets its standing test, the reproduction steps no longer produce the symptom.

Run them. Every one must fail because the behaviour doesn't exist yet. A test that passes asserts nothing or covers something already shipped, so sharpen it. A test that errors is broken, not red, so fix the typo or halt on a missing dependency.

A behaviour no automated test can reach is not a reason to skip it. Halt and name it. An `effort:minor` ticket with an untestable behaviour was mislabelled, and is `trivial` at most.

Commit the tests:

```
Test #<N>: <ticket title>

Red.
Issue: #<N>
```

**Completion criterion:** every Behaviour line covered by a test, every test observed failing for the right reason, one commit.

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

Each of these stops the session before push. Describe the failure in plain English, which test, the evidence, your best guess at the cause stated as a guess, and offer the real options: a hint from the user, a spec amendment per `../pr-ticket/ticket-pr.md` when the ticket itself is wrong, relabelling to the effort level the failure points at and taking that route, a `/challenge-pcr` session when a PCR is the block, or stopping here.

- **No progress.** The same test fails with the same evidence two passes running.
- **The ticket contradicts itself.** Two behaviours can't both be true.
- **A record blocks it, or a decision is needed.** A PCR or ADR the only workable implementation would breach, or a call a future reader could undo by accident. Name it. Never code around it, never edit a record, and never write one other than a found ADR; the ticket was mislabelled, so relabel it `effort:major` and run `/architect-ticket <N>`.

## 5. Refactor

Shape only, never behaviour. Behaviour includes what callers can observe behind an unchanged signature, such as the order of a returned list, an error message's text, a default value, or timing. Read every changed non-test file against the whole `docs/pcr/` and `docs/adr/` sets and against `../refactor-ticket/code-standards.md`, read from that skill's directory, never searched for in the repo. A record overrides the baseline. Tests are exempt. This station writes no argued records and amends none; a diff that needs one is the halt above. The one record it writes is a found ADR, per `../architect-ticket/RECORD-FORMAT.md`, for each fence comment the comment smell moves out of the code. Delete the comment in the same commit.

Re-run the tests from step 3 plus the neighbouring tests. Back to red means the edit changed behaviour, so revert it. Then commit once:

```
Refactor: <ticket title>

Issue: #<N>
```

A found ADR adds `Comment in <file> moved to ADR-NNNN` to the body.

Update `CONTEXT.md` if the branch shifted a domain term and the file exists, and `README.md` only if a contributor now needs to run or configure something new. Fold either into the refactor commit.

**Completion criterion:** every changed non-test file read against `docs/pcr/`, `docs/adr/`, and the baseline, each finding fixed, affected tests green, one commit.

## 6. Push and mark the PR ready

Rewrite the ticket PR's description from scratch and mark it ready for review:

```
git push -u origin <branch>
gh pr edit <PR> --title "<PR title>" --body-file <file>
gh pr ready <PR>
```

PR body, this shape:

```
> *This was implemented unattended by AI with execute-ticket. Review the diff before merging.*

Closes #<N>

## Summary
...

## Evidence
...

## Merge danger
...
```

Write the title, Summary, Evidence and Merge danger per `../pr-ticket/pr-shape.md`, read from that skill's directory, never searched for in the repo. Settle the title after Merge danger, since the breaking call reads Blast radius. List every amendment note under a `For the reviewer` heading, one line each, linking the note. Run the squash merge check from the same file for the report. Check the body against `unslop`. Write it to a temp file outside the repo and pass it with `--body-file`.

Do not close the issue. `Closes #<N>` closes it on merge, and merging is the review.

## 7. Report

Close with these lines and nothing after them:

```
Branch    42-fix-expired-session
Tests     3 added green, 5 neighbouring green
Commits   5
Title     fix: Expire sessions after idle timeout
PR        https://github.com/owner/repo/pull/57
Merge     squash with PR title
```
