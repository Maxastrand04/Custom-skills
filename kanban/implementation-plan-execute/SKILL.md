---
name: implementation-plan-execute
description: Drive an implementation plan to completion through the TDD loop, inline against the plan's
  binding `## Public interface`. Prerequisites gate the run, Red writes the acceptance tests and confirms
  they all fail, Green implements, and Verification runs them, looping back to Green until the suite is
  green. Then the work is committed and code quality is left to a separate code-review session. Use when
  user says "implementation-plan-execute", "implement the plan", "run the implementation plan", or invokes
  /implementation-plan-execute.
---

# implementation-plan-execute

You drive an implementation plan to completion, implementing each phase inline in the main thread. The plan's `## Public interface` is the **contract**, so implement exactly those names, parameters, and return values. Behind it you have full freedom. No implementation choice needs approval, and a separate code-review session judges the code on the commit afterward.

**The plan runs the TDD loop:**

1. **`Phase 0: Prerequisites` checks the ground.** Every pillar the plan stands on but does not build is confirmed present and working. The plan names the pillars; you decide how to confirm each one.
2. **`Phase 1: Red` writes the acceptance tests and runs them.** Every one must go red. No production code is written in this phase.
3. **The Green phases write the implementation** against `## Public interface`, until those tests pass.
4. **`Phase N: Verification` runs every Red test** and checks the implementation against every acceptance criterion.
5. **Green and Verification loop** until the suite is green. Then the work commits.

Tests run in exactly three places: confirming a Phase 0 prerequisite, the end of Red, and Verification. Nowhere else. No phase is smoke-checked as it completes, and no scratch script runs after an edit.

**Point, don't paste.** Read `## Acceptance criteria` out of the plan file when you need it. Never paste a copy of it into your own response, and never paste one into a subagent brief. A pasted block repeats verbatim across every retry, and that repetition accumulates in your context, which makes it the single largest avoidable driver of context growth over a multi-phase run.

**Terse verdicts only.** After a phase finishes or a Verification result comes back, state the one-line verdict, such as "Phase 2: ✅ done" or "Verification pass 2: AC-3 failing, back to Green", and move on. Don't re-paste a report, re-summarize a prior phase, or restate plan content the file already holds. The plan file's checkboxes are the sole source of truth for cross-phase state, so reason from them, not from scrollback.

---

## Input

1. **Plan reference**, meaning `plan N.N` anywhere in the invocation message. If absent, list `implementation_plans/` and pick the file with the highest `N.N` prefix.
2. Confirm the chosen plan with the user before doing anything else.

---

## Plan precondition check

Confirm `## Public interface` exists, `## Phase 1: Red` is the second phase, and `## Phase N: Verification` is the last phase with its acceptance-criteria rows. If any is missing, fail loud and halt:

> This plan predates the current plan format, which needs a `## Public interface` contract, a mandatory `Phase 1: Red`, and a mandatory final Verification phase. Re-plan with `/implementation-planning`.

---

## Branch checkout

Read `**Branch:**` from the plan and confirm you are on it before any code is written. `implementation-planning` already created it and wrote the plan there, so the normal case is that it exists and is checked out. Switch to it if not, and create it with `git checkout -b` only if it is genuinely absent, which happens with a hand-written plan. All Red, Green, and Finalization work happens on this branch. If the working tree carries unrelated uncommitted changes, surface that before switching.

---

## Bootstrap exploration sweep

After the precondition check and before Phase 0, dispatch **one `Explore` subagent on haiku** to summarize the files the plan touches, so you never read source just to get oriented.

- **Brief:** *"Collect every file named in a `File` cell across the plan's task tables. For each that exists, return its current shape, meaning top-level classes and functions and public surface, where it lives in the directory tree, and any obvious patterns or conventions in use. Do not read CONTEXT.md or unrelated files. Return a structured summary, one section per file."*
- Write the result to `{EXPLORATION_SUMMARY_PATH}`, for example `implementation_plans/.exploration-summary_N.N.md`. Never write it into the plan file, and never quote it back into your response. Read your own scoped slice from it directly before implementing a phase.
- **Refresh per phase.** At the start of each phase **after Phase 1**, including a Green repair pass the loop sends you back to, re-dispatch the same brief scoped to only the files the previous phase modified, and overwrite the matching entries. Don't re-read the whole file to do it.
- **Skip the refresh before Verification.** It writes no code, so the summary is still accurate.
- **Delete `{EXPLORATION_SUMMARY_PATH}`** during Finalization. It's scratch, not a plan artifact.

---

## Phase 0: Prerequisites

The gate between planning and code. **Red does not start until it passes.** It answers one question: is every pillar this plan stands on there and working?

The plan lists the pillars and stops there, on purpose. **How to confirm each one is yours to decide**, row by row, the same way everything behind `## Public interface` is.

- **Let the row's verb set the bar.** A row saying something *exists* is settled by finding it, and the exploration summary is usually enough. A row saying something *works* is not settled by finding it, because a symbol existing is not that thing working. Confirm those by running the existing tests that cover them, which is code this plan didn't write and doesn't own.
- **Ask when a row is ambiguous.** If you can't tell what would count as confirming it, or two readings would send you to check different things, put the question to the user before checking anything. Don't guess, and don't quietly check the easier reading.
- **Record what you did**, one line per row, so the check is visible rather than assumed.
- **A row flips ⬜ to ✅ only on a check you ran**, never on the plan having asserted it. Phase 0 exists precisely because the plan was written against an older tree.
- **Add rows you find.** If implementing would clearly need a pillar the plan didn't list, add it and check it. The list is the planner's best effort, not a closed set.
- If Phase 0 reads `None`, the plan stands on nothing pre-existing. Confirm the test framework below and move on.

**One standing check, on every plan:** a test framework exists and its command is known. Detect the runner from `package.json` at `scripts.test`, `pyproject.toml`, `Cargo.toml`, a `Makefile` `test` target, or the language default, and state the command. A project with no framework has nowhere to put the Red tests. Run nothing beyond what a prerequisite row calls for. The Red tests don't exist yet, and the rest of the suite is the reviewer's business.

**Completion criterion:** every prerequisite row is ✅ with an observed check and a one-line record behind it, and the runner command is named.

**Any missing or broken prerequisite halts the run.** Report which row failed and what you saw. That thing has to be implemented or fixed before this plan can proceed, which is a decision for the user: fold it into this plan, split it into its own, or stop here. Don't build the missing prerequisite yourself, don't stub it, and don't route around it.

---

## Phase loop

**Read `## Public interface` once, up front.** It is the spec for both the Red tests and the Green code. Never change a signature silently. If the contract itself proves wrong or incomplete mid-run, **stop and take it to the user**.

**Context discipline.** Every Read and Edit happens in your own thread, across the whole plan, in one continuous conversation. There is no per-phase subagent boundary for implementation. Don't pile incidental waste on top of that:
- Use the **Exploration summary file** instead of re-reading whole files to see current shape.
- Read only the exact region you're about to change, grepping to locate and then calling `Read` with `offset` and `limit`, unless the file is already short.
- Don't paste implemented code or diffs into your response. The `Edit` or `Write` call is the record. Name the files touched in one line and move on.

For each feature phase, in order: flip every task row ⬜ to 🟡, implement the rows inline, then flip 🟡 to ✅ once every row is done. Proceed directly to the next phase. Nothing runs between one Green phase and the next.

**Phase 1: Red** uses the same mechanics, with three differences:
- Its rows name a **test function and a file, and nothing else.** For each row, find the `AC-N` whose `Verify:` clause names that test and derive the assertions from that criterion. The plan deliberately doesn't spell them out.
- Call the code through `## Public interface` exactly as written. These tests are what pin the contract. Write no production code in this phase.
- **The phase ends by going red.** Once every row is written, run them and read the output. Each must fail because the behaviour doesn't exist yet. A test that **passes** means it asserts nothing real or the feature already ships; a test that **errors on a typo, a bad import, or a missing fixture** is broken rather than red. Either way, fix the test and re-run. Red is done only once every named test fails for the right reason.

**Green phases** implement against the same contract. Where a row says to copy a stub from `## Public interface`, copy the signature and docstring in verbatim and replace the `NotImplementedError` body. Don't retype a signature from memory.

**Green runs nothing.** A Green phase finishes when its rows are written, not when something passes. Resist checking your work by executing it. Verification does that, and the loop back from it is how a shortfall gets fixed.

**Status-flip exceptions.** Prerequisite rows flip ✅ on a confirmed check, Red rows flip ✅ only once the test is written and observed failing, and Verification rows flip ✅ only on a green test run. Those are the only flips your own judgment doesn't authorise.

---

## Verification phase loop

Run Verification yourself, in the main thread. No subagent is dispatched here.

Read `## Acceptance criteria` from the plan file, then work through **every** `AC-N`, without stopping at the first failure. Failures surface as a set, so one Green pass can answer all of them.

- **Automated criteria.** Run the exact test named in the criterion's `Verify:` line, the one written during `Phase 1: Red`. Record a pass or a failure with its evidence.
- **`(manual)` criteria.** No test was written for these. Record what the user needs to look at, in one line.

Then judge:

- **Any automated criterion failed.** Apply the Green loop below.
- **Every automated criterion passed, manual criteria remain.** List each to the user and ask for confirmation. Only then can those rows flip ✅.
- **Every criterion green.** Flip the rows ✅ and proceed to Finalization.

Report one line per criterion. Don't paste runner output for a criterion that passed; a failure is the only thing worth quoting in full.

### Green loop

A failure sends you back to Green, not to the user:

1. **Reopen what the failures implicate.** Flip the failing Verification rows back to ⬜, and the Green rows behind them back to 🟡. Leave passing rows alone.
2. **Run a Green repair pass** over exactly those rows, inline, with the failure evidence as context. Same rules as any Green phase: implement against `## Public interface`, change no signature, run nothing.
3. **Re-run Verification in full**, every `AC-N` again rather than only the ones that failed, since a repair can break a criterion that was green.
4. Repeat until the suite is green.

**Track the pass number** and report it, as in "Verification pass 3: AC-2 still failing", so a loop that isn't converging shows itself.

### Loop exits

Two things stop the loop and go to the user instead, because Green cannot fix either:

- **The fix would need an `AC-N` or a `## Public interface` change.** Both are single sources of truth and are never silently amended. Say which one you'd change and why, and wait for explicit approval.
- **No progress.** The same `AC-N` fails with the same evidence two Green passes running. Looping a third time would spin, so stop and report what you tried.

On either exit, describe the failure in plain English: which `AC-N`, the evidence, and whether it reads as an implementation bug, a wrong or stale test from Red, or a gap in the contract. State your best guess of the cause without asserting it, then ask what should happen next. Offer the real alternatives: keep looping with a hint they supply, redo a phase they name, fix it themselves, amend the criterion or the contract, or stop the plan here.

---

## Finalization step

This is not a phase. It runs no tests and has no rows in the plan file. It is bookkeeping that marks the plan complete and propagates the result outward. Run in order, only once every Verification row is ✅:

1. **Update the GitHub issue, on from-issue plans only.** If the plan title carries an issue reference in `(#N)` form, run `gh issue comment` on that issue with the plan filename and link, a checklist of every `AC-N` as `[x]` with its one-line evidence from Verification, and any manual criteria the user confirmed, under "Manually verified by user". Then run `gh issue close <N>`.
2. **Mark the matching task in `project_plan.md`, on from-issue plans only.** Locate the row whose leading `#` cell equals the plan slot `N.M` and flip its last Status cell to ✅. Every other byte is preserved, so do not rewrite the table, touch epic goals, or alter another row.

   **Guard:** if `project_plan.md` doesn't exist or no `N.M` row is found, skip silently and record it in the artifacts line, as in `project_plan.md: no row for 5.6, skipped`. The issue still closes regardless.
3. **Update `CONTEXT.md`** at the project root if it exists. Skip if not, and don't create one. Scan the completed plan for domain terms, relationships, or vocabulary the implementation introduced or shifted, and revise the Language and Relationships entries to match shipped reality. Match the file's existing style.
4. **Update `README.md`** only if the change alters something a new contributor needs to run or use the project, such as a new entry point, a new install or run command, or changed configuration. Skip internal-only changes, and don't invent README content.
5. **Commit the work** on the plan's branch, now that code and docs are final. Stage everything and commit with a lean message. The subject is the plan's title, and the body points to the plan file and, on from-issue plans, names the issue as the reviewer's source of truth. Don't pad it with a change summary; the plan and issue already hold that.

   ```
   <plan title>

   Plan: implementation_plans/<slot>_<slug>.md
   Issue: #<N>        # from-issue plans only, omit the line otherwise
   ```

   Do not push unless the user asks.
6. **Output one line per artifact touched**, such as `Closed #42`, `project_plan.md: flipped 5.6 to ✅`, `Updated CONTEXT.md`, `README.md unchanged`, and `Committed <sha> on <branch>`. Then announce the plan complete, and that `review-diff` should now clean up the committed diff.

Edit `CONTEXT.md` and `README.md` directly, with the same authority as plan-file edits. Issue comments use `gh issue comment`.
