---
name: pr-ticket
description: Pushes a finished branch, rewrites its PR into a body a reviewer can read cold, written from the diff and commits, and marks it ready unless the reviewer has items to tackle first. Use whenever a branch is ready for review, or you are about to open or finish a PR for one. Runs in a fresh subagent.
context: fork
agent: general-purpose
model: sonnet
---

# pr-ticket

You run in a fresh context. Whoever started you may know things about this branch, but you don't, and that is on purpose. Everything you write comes from the issue, the PR comments, the commits and the diff. Any arguments you were given name the issue number, the branch or the base.

The branch is finished and committed. You push it, rewrite its **ticket PR** from scratch, and mark it ready for review when nothing in it needs tackling first. The body is for a reviewer who never read the ticket or the commits. They should see what changed, why the tests prove it, and what a bad merge would break, before they open the diff.

**You never edit code or tests.** A problem you find goes in `For the reviewer`, not into a commit.

`pr-shape.md` and `ticket-pr.md` sit beside this `SKILL.md`. Read both from this skill's directory, never from the repo. You never amend the Spec, so from `ticket-pr.md` you only need Open or reuse it, Where notes go and Current Spec.

**You never stop to ask.** Where a step or `ticket-pr.md` would ask the user something, take the way forward the step names, write the PR anyway, and put the open question in `For the reviewer` as a yellow item. The reviewer tackles it on GitHub. The only halts are Committed and Green in step 1, and a PR that already merged per `ticket-pr.md`.

## 1. Pin the work and check the handoff

Take the issue number from the arguments, or else from the branch name, which carries it. Use the current branch unless the arguments name one. Fetch the ticket with `gh issue view <number> --comments`, read as the current Spec in `ticket-pr.md`. With no number anywhere, carry on as No ticket below says.

The base is `main` unless the arguments name another.

Open or reuse the ticket PR per `ticket-pr.md`, and note whether it is a draft with `gh pr view <PR> --json isDraft`. When only a closed PR exists, leave it closed. Open a new draft and add a yellow item linking the closed one.

**No ticket.** Write the PR from the diff and the commits alone. The Summary and every behaviour come from the code, in its own words, and the title follows `pr-shape.md` with a type and short title taken from what the diff does. Leave out the `Closes #<N>` line, and skip every `ticket-pr.md` step that needs the issue number. Add a yellow item: `No ticket linked, so nothing checked this branch against a spec.`

Halt unless both checks hold, naming the one that failed:

- **Committed.** `git status --porcelain` is empty. Never commit someone else's leftovers to make it so.
- **Green.** The whole suite passes. If not, say which tests fail and stop. With no suite in the repo, record that for Evidence and carry on.

Keep the suite's pass count for Evidence. Run the squash merge check from `pr-shape.md` and keep its result for the report. It never halts.

## 2. Read the branch

- **The ticket**, for the why and its words.
- **The commits.** `git log <base>..HEAD --format='%h %s%n%b'`. A commit body that records a decision, such as an `Amends ADR-` line, says what was settled.
- **The diff.** `git diff <base>...HEAD`, read in full, so the Summary describes the code and not the commit messages.
- **The tests.** Find the tests that turned green on this branch, as `pr-shape.md`'s Evidence says. Then compare every test file the diff adds or moves with where and how the repo's other tests live. A test file off the project's convention, such as a per-ticket acceptance file left beside the module tests, is a yellow reviewer item.
- **The review note.** A comment on the issue or the ticket PR that reports a review of this branch, such as one opening with a heading that names a review, or a GitHub review on the PR. Read them with `gh issue view <N> --json comments`, `gh pr view <PR> --json comments,reviews`. Take the newest. If the newest commit on the branch, `git log -1 --format=%cI`, is later than the note's `createdAt`, the note no longer covers `HEAD`. Compare them as times, not strings, since git prints a local offset and GitHub prints UTC.
- **Reviewer items.** Every `For the reviewer` line in the issue and ticket PR comments, plus the note's findings left unfixed. Add one line per amendment note, naming the Spec lines it changed and linking the note. An item about code outside the ticket's scope that the change breaks moves to Blast radius instead.

## 3. Write the body

Title per `pr-shape.md`, such as `feat: (3.2) Add OAuth login`.

```markdown
> *Written by AI from the branch's commits and diff. Review the diff before merging.*

Closes #<N>

## Summary
...

## Evidence
...

## Merge danger
...

## For the reviewer
...
```

Write Summary, Evidence, Merge danger and `For the reviewer` per `pr-shape.md`. Copy each reviewer item from its comment so it reads on its own, and sort it into its colour group.

Every body says where the review stands, in `For the reviewer`:

- **A note that covers `HEAD`.** A green item linking it.
- **A note older than the newest commit.** A yellow item: `The review note at <link> predates <short sha>, so the later commits went unreviewed.`
- **No note.** A yellow item: `No review note on this branch.`

**Don't wait for approval.** Once the body is written, go straight to step 4. The user reads the body on the PR, and the PR is the review.

## 4. Push, rewrite and mark ready

Replace the ticket PR's title and description:

```
git push -u origin <branch>
gh pr edit <PR> --title "<PR title>" --body-file <file>
```

Then the colour groups in `For the reviewer` decide the PR's state:

- **No red or yellow item.** Mark a draft ready with `gh pr ready <PR>`.
- **Any red or yellow item.** The PR stays a draft. If it was already marked ready, turn it back with `gh pr ready <PR> --undo`. The user reads the items on GitHub and marks it ready once they're dealt with.

Write the body to a temp file outside the repo, so nothing stray lands in the working tree. Never close the issue. `Closes #<N>` closes it on merge, and merging is the user's call.

## 5. Report

Close with these lines and nothing after them. With no suite in the repo, the Suite line reads `none in repo`. The PR line adds `, marked ready`, or `, draft, <count> items to tackle` when red or yellow items kept it a draft. When the squash merge check failed, the Merge line says what else is allowed, such as `merge commits allowed, the prefix can miss main`. The Review line reads `current`, `stale` or `none`.

```
Branch    42-fix-expired-session, pushed
Suite     green, 214 tests
Title     feat: (3.2) Add OAuth login
PR        https://github.com/owner/repo/pull/57
Merge     squash with PR title
Review    none
Reviewer  2 items
```
