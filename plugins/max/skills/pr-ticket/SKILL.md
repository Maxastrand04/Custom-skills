---
name: pr-ticket
description: Last station. Pushes the folded ticket branch and opens a PR whose body a reviewer can read cold, written from the commits. Runs after unit-test-ticket.
---

# pr-ticket

The last station on the board. `unit-test-ticket` committed the fold, so the branch is finished, green, and still local. You push it and open the PR. The body is for a reviewer who never read the ticket or the commits. They should see what changed, why the tests prove it, and what a bad merge would break, without opening the diff.

**You never edit code or tests.** A problem you find goes in `For the reviewer`, not into a commit.

The body's three sections follow `pr-shape.md`, the file beside this `SKILL.md`. Read it from this skill's directory, never from the repo. Word every halt and report to the user per the `gloss-me` skill, and check the body against `unslop`. The body itself carries no gloss blocks, since its reader isn't you.

## 1. Pin the work and check the handoff

The branch carries its **GitHub issue number** in the name. Take the current branch, or the one the user names, extract the number, and fetch the ticket with `gh issue view <number> --comments`. If the name carries no number, ask the user which issue this is.

The base is `main` unless the user names another. Halt unless all four hold, naming the one that failed:

- **Folded.** `git log <base>..HEAD` has a commit whose subject starts `Tests #<N>: tidy and fold`. If not, say to run `$max:unit-test-ticket` first.
- **Committed.** `git status --porcelain` is empty. Never commit someone else's leftovers to make it so.
- **Green.** The whole suite passes. If not, say which tests fail and stop. Red never gets a PR.
- **No PR yet.** `gh pr list --head <branch> --state open` is empty. If one exists, offer to rewrite its body instead, and on yes skip to step 3 with `gh pr edit` in place of `gh pr create`.

Keep the suite's pass count for Evidence.

## 2. Read the branch

- **The ticket**, for the why and its words.
- **The commits.** `git log <base>..HEAD --format='%h %s%n%b'`. The `Architect #<N>:` commit is Before. Its body and `Amends ADR-` lines say what was decided.
- **The diff.** `git diff <base>...HEAD`, read in full, so the Summary describes the code and not the commit messages.
- **The fold.** The `Tests #<N>: tidy and fold` commit and `unit-test-ticket`'s issue comment map each acceptance test to its file at `HEAD`.
- **Reviewer items.** Every `For the reviewer` line in the issue comments: bugs found and deleted, undefined behaviour, design worsened for testability.
- **`CONTEXT.md`**, if the repo has one, for the terms the Summary should use.

## 3. Write the body

Title: the ticket's title.

```markdown
> *Implemented by AI through the kanban chain. A human approved the interface and the tests. Review the diff before merging.*

Closes #<N>

## Summary
...

## Evidence
...

## Merge danger
...

## For the reviewer

- <item, copied from the issue comment, each readable on its own>
```

Write Summary, Evidence and Merge danger per `pr-shape.md`. Leave `For the reviewer` out when there are no items.

**Don't wait for approval.** Once the body passes `unslop`, go straight to step 4. The user reads the body on the PR, and the PR is the review.

## 4. Push and open

```
git push -u origin <branch>
gh pr create --base <base> --title "<ticket title>" --body-file <file>
```

Write the body to a temp file outside the repo, so nothing stray lands in the working tree. Never close the issue. `Closes #<N>` closes it on merge, and merging is the user's call.

## 5. Report

Close with these lines and nothing after them except `gloss-me`'s footer:

```
Branch    42-fix-expired-session, pushed
Suite     green, 214 tests
PR        https://github.com/owner/repo/pull/57
Reviewer  2 items
```
