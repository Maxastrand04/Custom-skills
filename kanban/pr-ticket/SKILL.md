---
name: pr-ticket
description: Last station. Checks the handoff the ticket's effort level asks for, pushes the branch, and rewrites the ticket PR into a body a reviewer can read cold, written from the commits, then marks it ready. Runs after unit-test-ticket or review-diff.
disable-model-invocation: true
---

# pr-ticket

The last station on the board, for every branch. On the kanban chain, `unit-test-ticket` committed the fold. Off it, `review-diff` left a review note. Either way the branch is finished and committed. You push it, rewrite its **ticket PR** from scratch, and mark it ready for review. The body is for a reviewer who never read the ticket or the commits. They should see what changed, why the tests prove it, and what a bad merge would break, before they open the diff.

**You never edit code or tests.** A problem you find goes in `For the reviewer`, not into a commit.

`pr-shape.md` and `ticket-pr.md` sit beside this `SKILL.md`. Read both from this skill's directory, never from the repo. You never amend the Spec, so from `ticket-pr.md` you only need Open or reuse it, Where notes go and Current Spec. Word every halt and report to the user per the `gloss-me` skill. The body itself carries no gloss blocks, since its reader isn't you.

## 1. Pin the work and check the handoff

The branch carries its **GitHub issue number** in the name. Take the current branch, or the one the user names, extract the number, and fetch the ticket with `gh issue view <number> --comments`, read as the current Spec in `ticket-pr.md`. If the name carries no number, ask the user which issue this is.

The base is `main` unless the user names another.

Read the ticket's `effort:<level>` label. With no effort label, ask the user for the level and use their answer for this run. Never add or change the issue's labels.

Open or reuse the ticket PR per `ticket-pr.md`, and note whether it is a draft with `gh pr view <PR> --json isDraft`.

The level picks the checks. Halt unless every check for it holds, naming the one that failed:

| Level | Checks |
|---|---|
| `major`, `medium` | Folded, Committed, Green |
| `minor` | Reviewed, Committed, Green |
| `trivial` | Reviewed, Committed, Green if the repo has a suite |

- **Folded.** `git log <base>..HEAD` has a commit whose subject starts `Tests #<N>: tidy and fold`. If not, say to run `/unit-test-ticket` first.
- **Reviewed.** A review note, per `../review-diff/review-note.md`, sits in the issue's comments or the ticket PR's. Read them with `gh issue view <N> --json comments` and `gh pr view <PR> --json comments`. Each comment carries its `body` and `createdAt`. Take the newest note. If none, say to run `/review-diff` first. If the newest commit on the branch, `git log -1 --format=%cI`, is later than the note's `createdAt`, the note no longer covers `HEAD`, so say to run `/review-diff` again. Compare them as times, not strings, since git prints a local offset and GitHub prints UTC.
- **Committed.** `git status --porcelain` is empty. Never commit someone else's leftovers to make it so.
- **Green.** The whole suite passes. If not, say which tests fail and stop. On `trivial` with no suite in the repo, record that for Evidence and carry on.

Keep the suite's pass count for Evidence. Run the squash merge check from `pr-shape.md` and keep its result for the report. It never halts.

## 2. Read the branch

- **The ticket**, for the why and its words.
- **The commits.** `git log <base>..HEAD --format='%h %s%n%b'`. On `major` or `medium`, the `Architect #<N>:` commit's body and `Amends ADR-` lines say what was decided.
- **The diff.** `git diff <base>...HEAD`, read in full, so the Summary describes the code and not the commit messages.
- **The fold**, on `major` or `medium`, found as `pr-shape.md`'s Evidence says.
- **The review note**, on `minor` or `trivial`. Its Suite line, Fixes and Found, not fixed rows, and any records it wrote or amended.
- **Reviewer items.** Every `For the reviewer` line in the issue and ticket PR comments: bugs found and deleted, undefined behaviour, design worsened for testability. Add one line per amendment note, naming the Spec line it changed and linking the note.
## 3. Write the body

Title per `pr-shape.md`, such as `feat: (3.2) Add OAuth login`.

```markdown
> *<header line>*

Closes #<N>

## Summary
...

## Evidence
...

## Merge danger
...

## For the reviewer

- <item, copied from its comment, each readable on its own>
```

The header line follows the route the branch took:

- **`major` or `medium`.** `Implemented by AI through the kanban chain. A human approved the interface and the tests. Review the diff before merging.`
- **`minor` or `trivial`.** `Implemented by AI in a session a human watched, then reviewed with review-diff. Review the diff before merging.`

Write Summary, Evidence and Merge danger per `pr-shape.md`. Leave `For the reviewer` out when there are no items.

**Don't wait for approval.** Once the body passes `unslop`, go straight to step 4. The user reads the body on the PR, and the PR is the review.

## 4. Push, rewrite and mark ready

Replace the ticket PR's title and description, then mark a draft ready for review:

```
git push -u origin <branch>
gh pr edit <PR> --title "<PR title>" --body-file <file>
gh pr ready <PR>
```

Run `gh pr ready` only when `isDraft` was true.

Write the body to a temp file outside the repo, so nothing stray lands in the working tree. Never close the issue. `Closes #<N>` closes it on merge, and merging is the user's call.

## 5. Report

Close with these lines and nothing after them except `gloss-me`'s footer. With no suite in the repo, the Suite line reads `none in repo`. The PR line adds `, marked ready` if it was a draft. When the squash merge check failed, the Merge line says what else is allowed, such as `merge commits allowed, the prefix can miss main`.

```
Branch    42-fix-expired-session, pushed
Suite     green, 214 tests
Title     feat: (3.2) Add OAuth login
PR        https://github.com/owner/repo/pull/57
Merge     squash with PR title
Reviewer  2 items
```
