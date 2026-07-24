---
name: implementation-plan-execute
description: Drive an implementation plan to completion — the model implements each Group inline with
  freedom on how, staying within the project's rule-ADRs in docs/adr/. The mandatory final
  Verification phase runs the acceptance-criteria tests once as the single source of truth for "does
  it work"; when they pass the work is committed, and architecture is left to a separate code-review
  session that enforces the rule-ADRs. Use when user says "implementation-plan-execute", "implement
  the plan", "run the implementation plan", "drive the plan group by group", or invokes
  /implementation-plan-execute.
---

# implementation-plan-execute

You drive an implementation plan to completion: you implement each Group inline, in the main thread, with freedom on *how* the code is written — staying within the project's rule-ADRs in `docs/adr/` (those named in the plan's `## Rules in play` apply directly). There is no per-Group architecture-approval gate; a separate code-review session enforces the rule-ADRs on the commit afterward.

**No Group or feature phase is tested as it completes.** Testing runs exactly once, in the plan's mandatory final `## Phase N — Verification`, and it checks one thing: that the code works — every acceptance criterion's test passes green. Architecture conformance is **not** checked here; a separate code-review session judges whether the shipped structure matches intent and needs refactoring. Verification is the single source of truth for "does it work"; nothing before it is verified by a subagent.

See `CONTEXT.md` at the repo root for canonical definitions of Group, Verification tester, the Red phase, and the Verification failure rule.

**Point, don't paste.** The Verification-phase tester dispatch gets the plan file's path and a scope label, and reads `## Acceptance criteria` from the plan file directly — never a pasted copy inside the dispatch prompt. Pasted blocks repeat verbatim across every retry, and that repetition lives in the Supervisor's own context, not the subagent's — the single largest avoidable driver of context growth over a multi-phase run. The Supervisor's job is dispatch and judgment, not restating plan content it already wrote to disk.

**Terse verdicts only.** After a Group finishes or a Verification result comes back, state the one-line verdict (e.g. "Group 2: ✅ done", "Verification: FAIL, escalating") and move on. Do not re-paste a report, do not re-summarize a prior phase, do not restate plan content the plan file already holds. The plan file's checkboxes are the sole source of truth for cross-phase state — reason from them, not from scrollback.

---

## Input

1. **Plan reference** — `plan N.N` anywhere in the invocation message. If absent, list `implementation_plans/` and pick the file with the highest `N.N` prefix.
2. Confirm the chosen plan with the user before doing anything else.

---

## Plan precondition check

After confirming the plan, confirm `## Rules in play` exists, `## Phase 1 — Red` exists as the second phase, and `## Phase N — Verification` exists as the last phase with its acceptance-criteria check.

If any is missing, fail loud and halt:

> This plan predates the current plan format (a `## Rules in play` pointer to `docs/adr/`, a mandatory `Phase 1 — Red`, and a mandatory final Verification phase). Re-plan with `/implementation-planning`.

---

## Branch checkout

Read `**Branch:**` from the plan and check it out before any code is written — create it if absent (`git checkout -b <branch>`), or switch to it if it exists. All Red and Green work, and the Finalization commit, happen on this branch. If the working tree carries unrelated uncommitted changes, surface that to the user before switching rather than writing over it.

---

## Bootstrap exploration sweep

After the plan precondition check and before Preflight, dispatch **one `Explore` subagent (haiku)** to summarize the current state of the files the plan touches. You don't read the source yourself just to get oriented — this offloads discovery so working context stays focused on judgment and the actual edits.

- **Brief:** *"Collect every file named in a `File` cell across the plan's task tables. For each that exists, return: current shape (top-level classes/functions, public surface), where it lives in the directory tree, any obvious patterns or conventions in use. Do not read CONTEXT.md or unrelated files. Return a structured summary, one section per file."*
- **Model:** `haiku`.
- Write the returned summary to `{EXPLORATION_SUMMARY_PATH}` (a scratch file, e.g. `implementation_plans/.exploration-summary_N.N.md` next to the plan) — never into the plan file, and never quoted back into your own response. Read your own scoped slice directly from this file before implementing a Group — never pasted into a prompt or a response.
- **Refresh per phase:** at the start of each feature phase **after Phase 1**, re-dispatch the same `Explore` brief but scoped to only the files modified during the immediately preceding phase. Overwrite the matching entries in the file — do not re-read the whole file back into context to do this, just replace the named sections.
- **Skip refresh on the Verification phase** — Verification writes no new code, so the prior summary is still accurate.
- **Delete `{EXPLORATION_SUMMARY_PATH}`** during Finalization — it is scratch, not a plan artifact.

---

## Phase 0 — Preflight

Preflight holds only genuine **blockers** — things that must be true before any code is written and that the plan couldn't settle on its own (an external credential provisioned, a repo or service created, a decision that could only be made at execution time). It is **not** an assumption-confirmation checklist; routine assumptions are not re-litigated here, so the run stays afk.

- If Phase 0 reads `None` (no blocker rows), announce "Preflight: none — starting Red" and go straight to Phase 1.
- Otherwise, for each blocker row state what must clear and let the user resolve it. A row needing a code fact may go to a `claude` subagent; it flips ⬜ → ✅ only once the blocker is actually cleared (user confirmation, or the fact coming back clear), not on discussion.
- You (the Supervisor) may edit the plan file directly to record a decision made here.

When every blocker is ✅ (or there were none), proceed to Phase 1 — Red.

`Phase 1 — Red` runs through the same per-Group mechanics as any other phase (below). The only difference is what's being written: failing (red) tests, not production code. Nothing checks that they actually fail at this point; the first time any test in this plan is executed is the Verification phase, where they're expected to have turned green.

---

## Group loop

**Implementer freedom.** You implement each Group inline with freedom on *how* the code is written; the only boundaries are the project's rule-ADRs in `docs/adr/`. There is no per-Group architecture-approval gate — no architecture is stated or approved before code. No functionality testing runs until the plan's final Verification phase, and a separate code-review session enforces the rule-ADRs on the commit afterward.

**Context discipline.** Every Read/Edit to write the code happens in your own thread, for every Group, across the whole plan, in one continuous conversation — there is no per-Group subagent boundary for implementation. Don't pile incidental waste on top of that:
- The **bootstrap exploration sweep** already wrote the **Exploration summary file** — use it instead of re-reading whole files to see current shape.
- If the plan's `## Rules in play` names rule-ADRs, read those files once up front so you implement within them — don't re-read them per Group.
- When implementing, read only the exact region you're about to change (grep to locate, then targeted `Read` with `offset`/`limit`) rather than whole files, unless the file is already short.
- Don't paste implemented code or diffs back into your own response — the `Edit`/`Write` call is the record. Name the files touched in one line and move on (per **Terse verdicts**).

For each feature phase, in order:

  For each Group in the phase, in order:

  Flip every task row in this Group ⬜ → 🟡, implement the Group's changes inline, then flip 🟡 → ✅ once every task is implemented. No tester runs per Group; correctness is checked once, later, in the Verification phase.

  **Rule gap:** if implementing forces a structural choice no rule-ADR covers *and* the choice is project-wide (it would recur beyond this plan), stop and flag it to the user — recommend adding a `codebase-rules` ADR — rather than baking in a silent precedent. A plan-local, throwaway choice needs no approval: decide it and move on; the reviewer catches problems against the rules.

  After the last Group in the phase is ✅, proceed directly to the next phase — no test runs between phases.

---

## Status-flip rule

- **Supervisor flips ⬜ → 🟡** when inline implementation of the Group starts.
- **Supervisor flips 🟡 → ✅** when inline implementation completes. No tester gates this flip for a feature-phase Group.
- **Exception:** Preflight blocker rows flip ✅ when the blocker clears, not on implementation completion.
- **Exception:** the Verification phase's acceptance-criteria check flips ✅ only on its tester's pass — see below. That is the one place a subagent, not the Supervisor's own judgment, authorises the flip.

---

## Verification phase loop

The plan's last phase is always `## Phase N — Verification`. No new code is written here, and no prior Group or phase was tested — this is the **single source of truth** for whether the code works. It checks acceptance criteria only; architecture is not swept here (a separate code-review session judges that).

Dispatch one `Explore` (haiku) tester with the brief:
   - `{PLAN_FILE_PATH}`, with instruction to read the plan's full `## Acceptance criteria` section itself — do not paste it into the prompt.
   - Instruction: *"For each `AC-N`, run the exact test named in its `Verify:` line (written during `Phase 1 — Red`) and return `[PASS] <evidence>` / `[FAIL: <evidence>]`. For criteria tagged `(manual)` (no test was written for these), return `[MANUAL CHECK REQUIRED: <reason>]` with a one-line description of what the user needs to look at."*
   - Supervisor judges:
     - All `[PASS]` (with any `[MANUAL CHECK REQUIRED]` items confirmed by the user) → flip the check ✅, proceed to Finalization.
     - Any `[FAIL]` → apply the **Verification failure rule** below.
     - Any `[MANUAL CHECK REQUIRED]` → list each one to the user, ask for confirmation. Only after user confirms can the check flip ✅.

### Verification failure rule

Verification is the only place a failure can occur, and it escalates on the **first** failing `AC-N` — there is no automatic retry and no attempt cap:

1. Stop immediately. Describe the failure to the user in plain English: which `AC-N` failed, the tester's evidence, and whether it looks like a bug in the implementation or a wrong/stale test from Phase 1.
2. State your best guess of the responsible Group (from earlier in the plan) and your reasoning, but don't assume it.
3. Ask the user what should happen next. Don't default to "retry" — offer it as one option alongside others: redo a specific Group (the user names it or defers to your guess), fix it themselves, amend the `AC-N` (requires their explicit approval — it is the single source of truth and is never silently amended), or stop the plan here.
4. Carry out whatever the user chose — a redo is a fresh inline implementation pass through that Group, with the failure report appended as context — then re-run the Verification check fresh to confirm.
5. If it fails again, escalate again the same way — every failure gets a fresh escalation to the user, not a silent retry.

A project-wide rule gap surfaced during a redo is handled inline (flag it, recommend a `codebase-rules` ADR), not as a Verification failure — see the Group loop above.

---

## Finalization step

This is **not a phase** — it has no Groups, no testers, and no rows in the plan file. It is Supervisor-only bookkeeping that marks the plan complete and propagates the result outward.

Run these in order, only after the Verification check is ✅:

1. **Update the GitHub issue (from-issue plans only).** If the plan title contains an issue reference (`(#N)`), post a `gh issue comment` to that issue containing:
   - Plan filename + link.
   - A checklist of every `AC-N` → `[x]` with the one-line evidence from the Verification tester's report.
   - Any `[MANUAL CHECK REQUIRED]` items the user confirmed, listed under "Manually verified by user".
   - Any new rule-ADR raised during execution (a flagged project-wide rule gap), listed under "New rules".

   Then close the issue: run `gh issue close <N>`.
2. **Mark the matching task in `project_plan.md` (from-issue plans only).** After the issue closes, locate the row in `project_plan.md` at the repo root whose leading `#` cell equals the plan slot `N.M` (e.g., `5.6`). Flip that row's last (Status) cell from its current value to ✅. Every other byte of the file is preserved — do not rewrite the table, touch sprint goals, or alter any other row.

   **Guard:** If `project_plan.md` does not exist, or no row with a leading `#` cell matching `N.M` is found, skip the flip silently and record it in the artifacts-touched line (e.g., `project_plan.md: no row for 5.6, skipped`). The issue still closes regardless.
3. **Update `CONTEXT.md`** at the project root if it exists. Skip if it does not — do not create one.
   - Scan the completed plan for new domain terms, relationships, or vocabulary the implementation introduced (or terms whose meaning shifted). Add or revise Language / Relationships entries to match the now-shipped reality.
   - Match the file's existing style (e.g., `**Term**:` blocks with `_Avoid_:` lines, relationship bullets).
4. **Update `README.md`** at the project root only if the implementation changed something a new contributor needs to know to use or run the project (new top-level entry point, new install/run command, changed configuration surface). If the change is internal-only, skip. Do not invent README content.
5. **Commit the work** on the plan's branch (see Branch checkout), only now that code and docs are final. Stage all changes and commit with a lean message a reviewer can anchor to: subject is the plan's title, body points to the plan file, and — on from-issue plans — names the issue as the reviewer's source of truth. Don't pad it with a change summary; the plan file and issue already hold that.

   ```
   <plan title>

   Plan: implementation_plans/<slot>_<slug>.md
   Issue: #<N>        # from-issue plans only — omit the line otherwise
   ```

   Do not push unless the user asks.
6. **Output one line per artifact touched.** Examples: `Posted AC checklist to #42`, `Closed #42`, `project_plan.md: flipped 5.6 → ✅`, `project_plan.md: no row for 5.6, skipped`, `Updated CONTEXT.md: added Verification phase`, `README.md unchanged`, `Committed <sha> on <branch>`. Then announce the plan complete, and that a code-review session should now check the committed diff against the rule-ADRs in `docs/adr/`.

Edit `CONTEXT.md` and `README.md` directly — same authority as plan-file edits. Issue comments use `gh issue comment`.
</content>
