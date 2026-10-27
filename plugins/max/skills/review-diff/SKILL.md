---
name: review-diff
description: Reviews any branch's committed diff against its ticket, the code smells, and the project's records, fixes what it finds, and leaves a review note on the PR or the issue. Runs before pr-ticket on branches refactor-ticket never saw.
---

# review-diff

The review for a branch however it was built: by hand, in an ordinary session, or by any station that skipped the TDD cycle. There may be no acceptance file and no test suite. You check the committed diff true-to-spec against the ticket, clean it against the code smells and the project's records, and leave a **review note** that `pr-ticket` reads.

**A smell or record fix never changes behaviour.** Before any such edit, ask whether a caller would see a difference. If one would, it is not a cleanup. A drift fix is the one edit here that changes behaviour, and it changes it only toward the ticket, with the user's approval. Wherever a step names no stop for the user, decide and act.

`review-note.md` resolves from this skill's directory, and so do `../refactor-ticket/code-standards.md`, `../unit-test-ticket/test-standards.md` and `../architect-ticket/RECORD-FORMAT.md`. Never read a same-named file from the repo.

Word every question and report per the `gloss-me` skill.

## 1. Pin the work

The user starts you with a ticket number. Without one, take it from the branch name, and if the name carries none, ask. Fetch the ticket with `gh issue view <N> --comments`. The base is `main` unless the user names another.

Find the runner command for the whole suite. A repo with no suite is normal here. Record that and carry on, since every fix still happens.

**Completion criterion:** ticket fetched, base known, suite command found or recorded as none.

## 2. Commit what's loose

The review reads committed work only, so the tree has to be clean first.

- **Untracked files.** List them and ask the user, file by file, include or leave. Wait for every answer.
- **Dirty tracked files**, plus every untracked file the user included, go in one commit: `WIP #<N>: work before review`. Leave files the user left alone, and name them in the note so `pr-ticket`'s clean-tree check doesn't surprise anyone.

`HEAD` after this step is the **pre-review commit**. Keep its short hash for the note, since `git diff <pre-review>..HEAD` is everything the review changed.

The diff is `git diff <base>...HEAD`, three-dot, against the merge-base. If it is empty, stop and say so. The **review scope** is every non-test file the diff changes.

**Completion criterion:** tree clean apart from files the user chose to leave, pre-review commit recorded, diff non-empty.

## 3. True-to-spec

**Make no edits in this step.** Work through the ticket's Spec one line at a time. A **drift finding** is a Spec line the diff doesn't meet, or something the diff does that the ticket never asked for.

- **Interface lines.** Each must match a piece the diff adds or alters. A missing or extra piece is a finding.
- **Behaviour lines.** Find the tests that cover the line and check they assert it, not something weaker. Where no test reaches it, read the code against the line directly.
- **Scope creep.** Check everything the diff adds against Out of scope and against the Spec as a whole. Work nobody asked for is a finding.

Don't run the suite here. You are reading for true-to-spec, not for a pass.

Zero findings means go to step 5. Otherwise print the findings as one table, `Spec line | Diff | Problem`, with no cell over 8 words, and ask the user, finding by finding, whether each is **intentional** or **unintentional**. Wait for every answer.

**Completion criterion:** every Spec line accounted for, and every finding has the user's verdict.

## 4. Record intentional drift

If any finding is intentional, post one `gh issue comment <N>` with a `For the reviewer` heading and one line per finding: the Spec line, what the diff does instead, and `intentional, user confirmed`. `pr-ticket` copies these lines into the PR body. Keep the comment's URL for the note.

No intentional finding means no comment.

## 5. Smells and records

Edit the code directly. Read every file in the review scope against three tiers, read per `../architect-ticket/RECORD-FORMAT.md`:

1. **PCRs in `docs/pcr/`.** A breach is a hard violation. Fix the code and cite `PCR-NNNN`. You never write, amend, or retire a PCR. When a PCR blocks a fix, leave the code, and put the item in Found, not fixed with ``run `$max:challenge-pcr` `` as the reason.
2. **ADRs in `docs/adr/`.** A breach is a hard violation too. Fix it and cite `ADR-NNNN`. Nothing pre-selects them, so take the whole set and judge which the changed files fall under. Read each one's **Decision** for what's required and its **Consequence** for what a breach looks like in a diff.
   - **When an ADR blocks a fix**, propose an amendment: show the user the rewritten Decision, Reason and Consequence, with your reason, and wait. On yes, amend it per the format file and make the fix. On no, the item goes in Found, not fixed.
   - **Write a new ADR when the diff introduces a shape neighbouring code will copy** and no record names it, such as a new layer, a new kind of module, or a dependency direction the first of its kind establishes. Run it through the ADR tests in the format file. Most reviews write none.
   - **Write a found ADR for every fence comment** the comment smell in `code-standards.md` moves out of the code, per the format file. Delete the comment in the same commit.
   - If the diff itself adds a file under `docs/adr/` or `docs/pcr/`, it belongs to whoever wrote it, and you leave it alone.
   - If neither directory exists, this step runs on the baseline alone.
3. **The baseline in `../refactor-ticket/code-standards.md`** applies everywhere no record covers. Apply its gates yourself.

**Run the suite after each fix.** On red, look at the failing test against `../unit-test-ticket/test-standards.md`:

- **Structure-sensitive.** It knew how the code was built, so your fix was right and the test was wrong. Rewrite it through the public interface, run the suite again, and keep the row for Reconciled tests.
- **Anything else.** The fix changed behaviour, so it was not a cleanup. Undo it, and put the item in Found, not fixed with the failing test as the reason.

With no suite, make each fix anyway and list it in the note for the user to check.

When every finding is fixed or recorded, commit the fixes, the adapted tests and any record together as `Review #<N>: smells and records`. An amended ADR adds `Amends ADR-NNNN: <why, one line>` to the body. A found ADR adds `Comment in <file> moved to ADR-NNNN`. No fixes means no commit.

**Completion criterion:** every file in the review scope read against the whole `docs/pcr/` and `docs/adr/` sets and every applicable baseline entry, each finding fixed or in Found, not fixed, the suite green or recorded as none, at most one commit.

## 6. Fix unintentional drift

For each unintentional finding, change the code toward the ticket: build what's missing, correct what's wrong, remove what nobody asked for. Run the suite after each fix. A test that turns red asserted the old behaviour, so adapt it to the fixed behaviour and keep the row for Reconciled tests.

**Leave every drift fix uncommitted.** These are the only behaviour changes the review makes, so the user reads them before they land.

No unintentional finding means go to step 8.

**Completion criterion:** every unintentional finding fixed in the working tree, the suite green or recorded as none.

## 7. Approve the drift fixes

Tell the user the drift fixes are in the working tree, name the files with `git diff --stat`, and ask them to review with `git diff`. Don't paste the diff into chat. Wait.

- **Approved.** Commit as `Fix #<N>: spec drift`.
- **Changes asked for.** Make them, re-run the suite, and ask again.
- **A fix rejected.** Revert it with its adapted tests, and put the finding in Found, not fixed with `user rejected fix`.

**Completion criterion:** the user approved, and the drift fixes are one commit.

## 8. Leave the note

Write the note per `review-note.md`, and check it against `unslop`. The note carries no gloss blocks, since its reader isn't you.

Check for a PR with `gh pr list --head <branch> --state open`.

- **A PR exists.** `git push`, then `gh pr comment <PR> --body-file <note>`.
- **No PR.** Don't push. Post it with `gh issue comment <N> --body-file <note>`.

Never close the issue. Merging the branch closes it.

## 9. Report

Five lines, then one line handing off. Don't repeat the note's tables in chat. The link is the record.

```
Note     <URL of the note>
Drift    3 found, 1 intentional, 2 fixed
Fixes    5 smells, 1 record breach, 1 found not fixed
Records  ADR-0009 written, ADR-0003 amended
Commits  wip b0c1d2e, review a1b2c3d, drift c9d8e7f
```

Then ``Next, run `$max:pr-ticket`.`` Nothing follows except `gloss-me`'s footer.
