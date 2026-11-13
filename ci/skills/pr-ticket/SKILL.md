---
name: pr-ticket
description: Headless last station for kanban-ci. Writes the PR title and the Summary, Evidence, Merge danger and For the reviewer sections of the PR body from the branch's commits, into files the loop rewrites the ticket PR with.
disable-model-invocation: true
---
<!-- synced-from kanban/pr-ticket/SKILL.md blob e7a3bf35c0fa78acc9edc7bc3630190c99bb446a -->

# pr-ticket, headless

The last station of a kanban-ci run. `unit-test-ticket` handed off to review, and the loop found the suite green. You write the PR title and the readable part of the ticket PR's new body. Its reader is the user, starting `/kanban-ci:review-ticket` in the morning. They should see what changed, why the tests prove it, and what a bad merge would break, before they open the diff.

**You never edit code or tests, and you never commit.** The loop resets the branch after you, so any edit is lost anyway.

The title, the three sections and `For the reviewer` follow `pr-shape.md`, the file beside this `SKILL.md`. Read it from this skill's directory, never from the repo. From `ticket-pr.md`, beside it too, you only need Current Spec. Check every line against `unslop`.

## Running headless

The loop starts you with `claude -p`. Nobody reads this session and nobody answers. Never ask a question and never wait.

- **The invocation** carries the issue number, the base branch and the ticket PR, as in `#42 base:main pr:57`. Under it are the paths to write the body and the title to, and the **suite summary**, the result of the whole suite run after `unit-test-ticket`. Default the base to `main`.
- **Never run the whole suite.** The suite summary is your After. If it doesn't say the suite passed, write nothing and stop. The loop falls back to its plain body. For the same reason, skip the coverage tool in Untested behaviour and read instead.
- **Never push, edit the PR, comment on the issue or the PR, or edit labels.** The loop owns GitHub.
- **Write only the body and title files.** No other file, in the repo or out of it. Skip the squash merge check. The loop has no report for it.

## 1. Read the branch

- **The ticket.** `gh issue view <N> --comments`, read as the current Spec in `ticket-pr.md`, for the why and its words.
- **The ticket PR.** `gh pr view <PR> --comments`, for each station's comment.
- **The commits.** `git log <base>..HEAD --format='%h %s%n%b'`. The `Architect #<N>:` commit is Before. The `Tests #<N>: tidy and fold` commit, or `unit-test-ticket`'s comment on the ticket PR, maps each acceptance test to its file at `HEAD`.
- **Reviewer items.** Every `For the reviewer` section in the commit bodies. Add one line per amendment note on the issue, naming the Spec line it changed and linking the note. An item about code outside the ticket's scope that the change breaks moves to Blast radius instead.
- **The diff.** `git diff <base>...HEAD`, read in full, so the Summary describes the code and not the commit messages.
- **`CONTEXT.md`**, if the repo has one, for the terms the Summary should use.

## 2. Write the body and title files

Write `## Summary`, `## Evidence`, `## Merge danger` and `## For the reviewer` per `pr-shape.md` to the body path, and nothing else. No title, disclaimer or `Closes` line. The loop adds those above your sections. Copy each reviewer item so it reads on its own, and sort it into its colour group. Leave `For the reviewer` out when there are no items.

Then write the title per `pr-shape.md` to the title path, as one line and nothing else, such as `feat: (3.2) Add OAuth login`. Settle it after Merge danger, since the breaking call reads Blast radius. The loop checks the line starts `feat` or `fix` and falls back to its own title, without `!`, when it doesn't.

Take the test count for Evidence from the suite summary when it gives one. Otherwise write `Whole suite green.` without a count.

## Report

Print these lines and stop:

```
Body      /tmp/pr-summary.md
Title     feat: (3.2) Add OAuth login
Sections  summary with sequence diagram, evidence 4 tests, merge danger two-way, reviewer 1 red 2 green
```
