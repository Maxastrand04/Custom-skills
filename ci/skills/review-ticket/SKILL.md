---
name: review-ticket
description: Interactive review of a kanban-ci PR. Walks the user through the handoff trail and every item left for the reviewer, applies the fixes they approve, and writes the issue comment a human developer reads.
disable-model-invocation: true
---

# review-ticket

The last station of a kanban-ci run, and the only one with a human in it. The loop ran implement, refactor and unit-test with nobody watching, and every call it made in the user's place is written down. Your job is to put those calls in front of the user, fix what they overrule, and leave a record a developer can read without opening the diff.

Word every question, item, and report per the `gloss-me` skill, and check everything you write, chat and issue comment alike, against `unslop`.

**The user approves every change here.** Anything may change, signatures and tests included, because the user is watching. One exception: a contract that is wrong at its core, meaning a boundary in the wrong place or an entry point that shouldn't exist, is not patched here. Say so and recommend closing the PR and running `/architect-ticket` again.

## 1. Pin the PR

Resolve the PR from the invocation, a number or URL, or from the current branch with `gh pr view`. Read it:

```
gh pr view <pr> --json number,title,body,isDraft,headRefName,baseRefName
```

Check out the head branch and pull it. Fetch the issue named on its `Closes #<N>` line with `gh issue view <N>`.

## 2. Read the trail

- **The handoff trail.** `git log <base>..HEAD --format='%h %s%n%b'`. Each commit's `Handoff-From` and `Handoff-To` trailers show the route the work took, backward moves included.
- **For the reviewer.** The PR body collects every station's items. Read them against the commits they came from.
- **The halt.** A draft PR stopped early. The body names the reason, and the last commit's body holds the station's own account.
- **The diff.** `git diff <base>...HEAD`. Read it in full before the walk, so every answer you give is grounded in the code.

## 3. Walk it with the user

Open with three lines: the status (finished, or halted and where), the route, and the number of items.

Then present the items as one numbered round, each with your recommendation, in this order:

1. **The halt**, if there is one.
2. **Visibility decisions** refactor-ticket made in the user's place. Those are the calls the interactive version asked about.
3. **Bugs** unit-test-ticket found and deleted the tests for.
4. **Spec fixes and decisions against the ticket**, such as stale tests rewritten, ADRs written or amended, and scope creep.
5. **Everything else** in For the reviewer.

Wait for the answers. Then offer a walk through the diff by module, for anything the user wants to look at that no item covered.

## 4. Apply

For each change the user approves:

1. Edit, then run the narrow tests that cover it: the module test file, or the single test.
2. For a bug that deserves its own ticket rather than a fix here, say so and point at `/new-ticket`.
3. Commit as `Review #<N>: <what changed>`, one commit per item, so the PR reads item by item. No handoff trailers; these commits never restart the chain.

Push when the user says the review is done. The project's own test workflow checks the PR on that push.

## 5. The issue comment

The commits were written for agents. The issue comment is for a developer who reads the issue months from now and never opens the diff. Draft it and show it to the user before posting:

- **What shipped**, in the ticket's words, a few lines.
- **Decisions that went against or beyond the ticket**, each with its reason.
- **What broke** and how it was fixed, if anything did.
- **What the next developer needs to know**: a new ADR, an open bug ticket, undefined behaviour left as is.

Leave out any heading with nothing under it. Post it with `gh issue comment <N>` only after the user approves.

## 6. Close out

- If the PR is a draft and the user says it's ready, `gh pr ready <pr>`.
- Remove `ci:queued` from the issue if it is still there.
- Never merge. That is the user's call, after the test workflow passes.

Close with these lines:

```
PR       #57, ready
Commits  review 3
Issue    commented #42
Next     merge after the test workflow passes
```
