---
name: pr-ticket
description: Headless last station for kanban-ci. Writes the Summary, Evidence and Merge danger sections of the PR body from the branch's commits, into a file the loop opens the PR with.
disable-model-invocation: true
---
<!-- synced-from kanban/pr-ticket/SKILL.md blob 28f3a62f7e1fe0b82ce8f55ea9013ffc755adc24 -->

# pr-ticket, headless

The last station of a kanban-ci run. `unit-test-ticket` handed off to review, and the loop found the suite green. You write the readable part of the PR body. Its reader is the user, starting `/kanban-ci:review-ticket` in the morning. They should see what changed, why the tests prove it, and what a bad merge would break, before they open the diff.

**You never edit code or tests, and you never commit.** The loop resets the branch after you, so any edit is lost anyway.

The three sections follow `pr-shape.md`, the file beside this `SKILL.md`. Read it from this skill's directory, never from the repo. Check every line against `unslop`.

## Running headless

The loop starts you with `claude -p`. Nobody reads this session and nobody answers. Never ask a question and never wait.

- **The invocation** carries the issue number and the base branch, as in `#42 base:main`. Under it are the path to write the body to and the **suite summary**, the result of the whole suite run after `unit-test-ticket`. Default the base to `main`.
- **Never run the whole suite.** The suite summary is your After. If it doesn't say the suite passed, write nothing and stop. The loop falls back to its plain body.
- **Never push, open a PR, comment on the issue, or edit labels.** The loop owns GitHub.
- **Write only the body file.** No other file, in the repo or out of it.

## 1. Read the branch

- **The ticket.** `gh issue view <N>`, for the why and its words.
- **The commits.** `git log <base>..HEAD --format='%h %s%n%b'`. The `Architect #<N>:` commit is Before. `Tests #<N>: tidy and fold` maps each acceptance test to its file at `HEAD`. Skip the `For the reviewer` sections. The loop copies those into the body itself.
- **The diff.** `git diff <base>...HEAD`, read in full, so the Summary describes the code and not the commit messages.
- **`CONTEXT.md`**, if the repo has one, for the terms the Summary should use.

## 2. Write the body file

Write `## Summary`, `## Evidence` and `## Merge danger` per `pr-shape.md` to the path the invocation names, and nothing else. No title, disclaimer, `Closes` line or `For the reviewer`. The loop adds those around your sections.

Take the test count for Evidence from the suite summary when it gives one. Otherwise write `Whole suite green.` without a count.

## Report

Print these lines and stop:

```
Body      /tmp/pr-summary.md
Sections  summary with sequence diagram, evidence 4 tests, merge danger two-way
```
