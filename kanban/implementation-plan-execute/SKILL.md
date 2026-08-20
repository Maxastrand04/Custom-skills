---
name: implementation-plan-execute
description: Drive an implementation plan to completion — the model implements each phase inline against
  the plan's binding `## Public interface`, with full freedom on how the code behind it is written. The
  mandatory final Verification phase runs the acceptance-criteria tests once as the single source of truth
  for "does it work"; when they pass the work is committed, and code quality is left to a separate
  code-review session. Use when user says "implementation-plan-execute", "implement the plan", "run the
  implementation plan", or invokes /implementation-plan-execute.
---

# implementation-plan-execute

You drive an implementation plan to completion, implementing each phase inline in the main thread. The plan's `## Public interface` is the **contract** — implement exactly those names, parameters, and return values. Behind it you have full freedom; no implementation choice needs approval, and a separate code-review session judges the code on the commit afterward.

**No phase is tested as it completes.** Testing runs exactly once, in the plan's mandatory final `## Phase N — Verification`, and checks one thing: every acceptance criterion's test passes green. It is the single source of truth for "does it work".

See `CONTEXT.md` at the repo root for canonical definitions of the Verification tester, the Red phase, and the Verification failure rule.

**Point, don't paste.** The Verification tester gets the plan file's *path* and reads `## Acceptance criteria` itself — never a pasted copy inside the dispatch prompt. A pasted block repeats verbatim across every retry, and that repetition lives in your context, not the subagent's — the single largest avoidable driver of context growth over a multi-phase run.

**Terse verdicts only.** After a phase finishes or a Verification result comes back, state the one-line verdict ("Phase 2: ✅ done", "Verification: FAIL, escalating") and move on. Don't re-paste a report, re-summarize a prior phase, or restate plan content the file already holds. The plan file's checkboxes are the sole source of truth for cross-phase state — reason from them, not from scrollback.

---

## Input

1. **Plan reference** — `plan N.N` anywhere in the invocation message. If absent, list `implementation_plans/` and pick the file with the highest `N.N` prefix.
2. Confirm the chosen plan with the user before doing anything else.

---

## Plan precondition check

Confirm `## Public interface` exists, `## Phase 1 — Red` is the second phase, and `## Phase N — Verification` is the last phase with its acceptance-criteria rows. If any is missing, fail loud and halt:

> This plan predates the current plan format (a `## Public interface` contract, a mandatory `Phase 1 — Red`, and a mandatory final Verification phase). Re-plan with `/implementation-planning`.

---

## Branch checkout

Read `**Branch:**` from the plan and confirm you are on it before any code is written. `implementation-planning` already created it and wrote the plan there, so the normal case is that it exists and is checked out — switch to it if not, and create it (`git checkout -b`) only if genuinely absent (a hand-written plan). All Red, Green, and Finalization work happens on this branch. If the working tree carries unrelated uncommitted changes, surface that before switching.

---

## Bootstrap exploration sweep

After the precondition check and before Preflight, dispatch **one `Explore` subagent (haiku)** to summarize the files the plan touches, so you never read source just to get oriented.

- **Brief:** *"Collect every file named in a `File` cell across the plan's task tables. For each that exists, return: current shape (top-level classes/functions, public surface), where it lives in the directory tree, any obvious patterns or conventions in use. Do not read CONTEXT.md or unrelated files. Return a structured summary, one section per file."*
- Write the result to `{EXPLORATION_SUMMARY_PATH}` (e.g. `implementation_plans/.exploration-summary_N.N.md`) — never into the plan file, never quoted back into your response. Read your own scoped slice from it directly before implementing a phase.
- **Refresh per phase:** at the start of each phase **after Phase 1**, re-dispatch the same brief scoped to only the files the previous phase modified, and overwrite the matching entries — don't re-read the whole file to do it.
- **Skip the refresh before Verification** — it writes no code, so the summary is still accurate.
- **Delete `{EXPLORATION_SUMMARY_PATH}`** during Finalization; it's scratch, not a plan artifact.

---

## Phase 0 — Preflight

Preflight holds only genuine **blockers** — things that must be true before any code is written and that the plan couldn't settle on its own. Routine assumptions are not re-litigated here, so the run stays afk.

- If Phase 0 reads `None`, announce "Preflight: none — starting Red" and go straight to Phase 1.
- Otherwise state what each blocker needs and let the user resolve it. A row needing a code fact may go to a `claude` subagent; it flips ⬜ → ✅ only once the blocker actually clears, not on discussion.
- You may edit the plan file directly to record a decision made here.

---

## Phase loop

**Read `## Public interface` once, up front** — it is the spec for both the Red tests and the Green code. Never change a signature silently: if the contract itself proves wrong or incomplete mid-run, **stop and take it to the user**.

**Context discipline.** Every Read/Edit happens in your own thread, across the whole plan, in one continuous conversation — there is no per-phase subagent boundary for implementation. Don't pile incidental waste on top of that:
- Use the **Exploration summary file** instead of re-reading whole files to see current shape.
- Read only the exact region you're about to change (grep to locate, then `Read` with `offset`/`limit`) unless the file is already short.
- Don't paste implemented code or diffs into your response — the `Edit`/`Write` call is the record. Name the files touched in one line and move on.

For each feature phase, in order: flip every task row ⬜ → 🟡, implement the rows inline, then flip 🟡 → ✅ once every row is done. Proceed directly to the next phase — nothing runs in between.

**Phase 1 — Red** uses the same mechanics, with two differences in what you write:
- Its rows name a **test function and a file, and nothing else.** For each row, find the `AC-N` whose `Verify:` clause names that test and derive the assertions from that criterion. The plan deliberately doesn't spell them out.
- Call the code through `## Public interface` exactly as written — these tests are what pin the contract. Write no production code, and run nothing: the first time any test executes is Verification, where it's expected to be green.

**Green phases** implement against the same contract. Where a row says to copy a stub from `## Public interface`, copy the signature and docstring in verbatim and replace the `NotImplementedError` body — don't retype a signature from memory.

**Status-flip exceptions:** Preflight rows flip ✅ when the blocker clears; Verification rows flip ✅ only on the tester's pass. Those are the only flips your own judgment doesn't authorise.

---

## Verification phase loop

Dispatch one `Explore` (haiku) tester:
   - Give it `{PLAN_FILE_PATH}` and instruct it to read the plan's `## Acceptance criteria` itself.
   - Brief: *"For each `AC-N`, run the exact test named in its `Verify:` line (written during `Phase 1 — Red`) and return `[PASS] <evidence>` / `[FAIL: <evidence>]`. For criteria tagged `(manual)` (no test was written for these), return `[MANUAL CHECK REQUIRED: <reason>]` with a one-line description of what the user needs to look at."*
   - Then judge:
     - All `[PASS]` → flip the rows ✅, proceed to Finalization.
     - Any `[FAIL]` → apply the **Verification failure rule**.
     - Any `[MANUAL CHECK REQUIRED]` → list each to the user and ask for confirmation. Only then can the row flip ✅.

### Verification failure rule

Verification is the only place a failure can occur, and it escalates on the **first** failing `AC-N`, every time — no automatic retry, no attempt cap:

1. Stop immediately. Describe the failure in plain English: which `AC-N` failed, the tester's evidence, and whether it looks like a bug in the implementation, a wrong or stale test from Phase 1, or a gap in `## Public interface`.
2. State your best guess of the responsible phase and your reasoning, but don't assume it.
3. Ask the user what should happen next. Don't default to "retry" — offer it alongside: redo a specific phase (they name it or defer to your guess), fix it themselves, amend the `AC-N` or the `## Public interface` contract (either needs their explicit approval — both are single sources of truth and are never silently amended), or stop the plan here.
4. Carry out their choice — a redo is a fresh inline pass through that phase with the failure report as context — then re-run Verification fresh. A repeat failure escalates again the same way.

---

## Finalization step

Not a phase — no testers, no rows in the plan file. Supervisor-only bookkeeping that marks the plan complete and propagates the result outward. Run in order, only once every Verification row is ✅:

1. **Update the GitHub issue (from-issue plans only).** If the plan title carries an issue reference (`(#N)`), `gh issue comment` that issue with: the plan filename + link; a checklist of every `AC-N` → `[x]` with its one-line evidence from the tester's report; any `[MANUAL CHECK REQUIRED]` items the user confirmed, under "Manually verified by user". Then `gh issue close <N>`.
2. **Mark the matching task in `project_plan.md` (from-issue plans only).** Locate the row whose leading `#` cell equals the plan slot `N.M` and flip its last (Status) cell to ✅. Every other byte is preserved — do not rewrite the table, touch epic goals, or alter another row.

   **Guard:** if `project_plan.md` doesn't exist or no `N.M` row is found, skip silently and record it in the artifacts line (`project_plan.md: no row for 5.6, skipped`). The issue still closes regardless.
3. **Update `CONTEXT.md`** at the project root if it exists — skip if not, don't create one. Scan the completed plan for domain terms, relationships, or vocabulary the implementation introduced or shifted, and revise the Language / Relationships entries to match shipped reality. Match the file's existing style.
4. **Update `README.md`** only if the change alters something a new contributor needs to run or use the project (new entry point, new install/run command, changed configuration surface). Internal-only changes: skip. Don't invent README content.
5. **Commit the work** on the plan's branch, now that code and docs are final. Stage everything and commit with a lean message — subject is the plan's title, body points to the plan file and, on from-issue plans, names the issue as the reviewer's source of truth. Don't pad it with a change summary; the plan and issue already hold that.

   ```
   <plan title>

   Plan: implementation_plans/<slot>_<slug>.md
   Issue: #<N>        # from-issue plans only — omit the line otherwise
   ```

   Do not push unless the user asks.
6. **Output one line per artifact touched** (`Closed #42`, `project_plan.md: flipped 5.6 → ✅`, `Updated CONTEXT.md`, `README.md unchanged`, `Committed <sha> on <branch>`). Then announce the plan complete, and that `review-diff` should now clean up the committed diff.

Edit `CONTEXT.md` and `README.md` directly — same authority as plan-file edits. Issue comments use `gh issue comment`.
