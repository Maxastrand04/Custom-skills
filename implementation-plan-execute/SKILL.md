---
name: implementation-plan-execute
description: Drive an implementation plan to completion — the model implements each Group inline,
  the user approves architecture per Group in real time. All testing — architecture and acceptance
  criteria — runs once, in the plan's mandatory final Verification phase, which is the single
  source of truth. Use when user says "implementation-plan-execute", "implement the plan", "run the
  implementation plan", "drive the plan group by group", or invokes /implementation-plan-execute.
---

# implementation-plan-execute

You drive an implementation plan to completion: you implement each Group inline, in the main thread, and the user reviews architecture per Group in real time before any code is written.

**No Group or feature phase is tested as it completes.** Testing — both architecture conformance and acceptance criteria — runs exactly once, in the plan's mandatory final `## Phase N — Verification`. That phase is the single source of truth; nothing before it is verified by a subagent.

See `CONTEXT.md` at the repo root for canonical definitions of Group, Verification tester, Write-acceptance-tests phase, and Verification failure rule.

**Point, don't paste.** Every Verification-phase tester dispatch gets the plan file's path and a scope label, and reads its own sections from the plan file directly — never a pasted copy of `## Acceptance criteria` or `## Architecture decisions` inside the dispatch prompt. Pasted blocks repeat verbatim across every retry, and that repetition lives in the Supervisor's own context, not the subagent's — the single largest avoidable driver of context growth over a multi-phase run. The Supervisor's job is dispatch and judgment, not restating plan content it already wrote to disk.

**Terse verdicts only.** After a Group finishes or a Verification result comes back, state the one-line verdict (e.g. "Group 2: ✅ done", "Verification: FAIL, escalating") and move on. Do not re-paste a report, do not re-summarize a prior phase, do not restate plan content the plan file already holds. The plan file's checkboxes are the sole source of truth for cross-phase state — reason from them, not from scrollback.

---

## Input

1. **Plan reference** — `plan N.N` anywhere in the invocation message. If absent, list `implementation_plans/` and pick the file with the highest `N.N` prefix.
2. Confirm the chosen plan with the user before doing anything else.

---

## Plan precondition check

After confirming the plan, grep it for `**Architecture decisions (Group N):**` inside every `### Group N` block under feature phases, confirm `## Phase 1 — Write acceptance tests` exists as the second phase, and confirm `## Phase N — Verification` exists as the last phase with its two Groups.

If any is missing, fail loud and halt:

> This plan predates the current plan format (per-group architecture binding, a mandatory `Phase 1 — Write acceptance tests`, and a mandatory final Verification phase). Re-plan with `/implementation-planning`.

---

## Bootstrap exploration sweep

After the plan precondition check and before Phase 0, dispatch **one `Explore` subagent (haiku)** to summarize the current state of the files the plan touches. You don't read the source yourself just to get oriented — this offloads discovery so working context stays focused on judgment and the actual edits.

- **Brief:** *"Read the files listed in `## Architecture decisions` → Files affected. For each file, return: current shape (top-level classes/functions, public surface), where it lives in the directory tree, any obvious patterns or conventions in use. Do not read CONTEXT.md or unrelated files. Return a structured summary, one section per file."*
- **Model:** `haiku`.
- Write the returned summary to `{EXPLORATION_SUMMARY_PATH}` (a scratch file, e.g. `implementation_plans/.exploration-summary_N.N.md` next to the plan) — never into the plan file, and never quoted back into your own response. Read your own scoped slice directly from this file before stating architecture (Step 1) — never pasted into a prompt or a response.
- **Refresh per phase:** at the start of each feature phase **after Phase 1**, re-dispatch the same `Explore` brief but scoped to only the files modified during the immediately preceding phase. Overwrite the matching entries in the file — do not re-read the whole file back into context to do this, just replace the named sections.
- **Skip refresh on the Verification phase** — Verification writes no new code, so the prior summary is still accurate.
- **Delete `{EXPLORATION_SUMMARY_PATH}`** during Finalization — it is scratch, not a plan artifact.

---

## Phase 0 — Interactive prerequisites

Phase 0 is **never** delegated to a tester. Walk it row-by-row with the user, grill-me style:

- For each Phase 0 row, restate the task in plain English and ask the user to confirm, decide, or supply the missing information.
- If a row requires a quick code check (e.g., "confirm no existing directory"), you may dispatch a `claude` subagent to gather the fact and report back, but the row only flips ✅ after the user confirms.
- You (the Supervisor) may edit the plan file directly to record decisions made during this walkthrough (e.g., a chosen value, a confirmed assumption).
- Flip the row ⬜ → ✅ on user confirmation.

When every Phase 0 row is ✅, announce "Phase 0 complete — starting Phase 1" and proceed.

`Phase 1 — Write acceptance tests` runs through the same per-Group mechanics as any other phase (below). The only difference is what's being written: failing (red) tests, not production code. Nothing checks that they actually fail at this point; the first time any test in this plan is executed is the Verification phase, where they're expected to have turned green.

---

## Group loop

**Architecture review is the user's role.** Neither you nor any subagent decides structure unilaterally — every Group's architecture is stated and approved before a line of code is written, and no functionality testing runs until the plan's final Verification phase.

**Context discipline.** There is no per-Group subagent boundary for implementation — every Read/Edit you do to write the code happens in your own thread, for every Group, across the whole plan, in one continuous conversation. That's the point (real-time architecture review needs the model that's about to write code in the room) and it cannot be delegated away, but don't pile incidental waste on top of it:
- The **bootstrap exploration sweep** (run once before Phase 0, refreshed per phase — see above) already wrote the **Exploration summary file**. Use it to state architecture in Step 1 — do not Read whole files just to describe their current shape.
- When implementing (Step 3), read only the exact region you're about to change (grep to locate, then targeted `Read` with `offset`/`limit`) rather than whole files, unless the file is already short.
- Don't paste implemented code or diffs back into your own response — the `Edit`/`Write` call is the record. Name the files touched in one line and move on (per **Terse verdicts**).

For each feature phase, in order:

  For each Group in the phase, in order:

  **Step 1 — State architecture**

  Read the Group's `**Architecture decisions (Group N):**` sub-block from the plan. Tell the user which AD-N items this Group follows and how the upcoming code will follow them. Wait for explicit user approval before writing any code.

  **Step 2 — Architecture rejection loop**

  If the user rejects the architecture statement, revise it and re-propose. Continue until the user gives explicit approval. No implementation step is reachable until the user approves.

  **Step 3 — Inline implementation**

  On approval: flip every task row in this Group ⬜ → 🟡 in the plan file. Implement the Group's changes inline. Once every task in the Group is implemented, flip 🟡 → ✅ directly — no tester runs per Group. A Group advances on architecture approval (Step 2) plus completed implementation (this step); correctness is checked once, later, in the Verification phase.

  **Mid-implementation architecture gap:** if, while implementing, you hit a structural choice the approved statement didn't cover, stop immediately — do not improvise. Surface the gap to the user in plain English with a recommendation. Wait for the user to either approve an AD addition/amendment (edit `## Architecture decisions` to add `AD-N+1` or amend an existing AD verbatim per the user's words) or redesign. Then resume implementation from where you stopped.

  After the last Group in the phase is ✅, proceed directly to the next phase — no test runs between phases.

---

## Status-flip rule

- **Supervisor flips ⬜ → 🟡** when the user approves architecture and inline implementation starts.
- **Supervisor flips 🟡 → ✅** when inline implementation completes. No tester gates this flip for a feature-phase Group.
- **Exception:** Phase 0 rows flip ✅ on user confirmation, not implementation completion.
- **Exception:** the Verification phase's own two Groups flip ✅ only on their tester's pass — see below. That is the one place a subagent, not the Supervisor's own judgment, authorises the flip.

---

## Verification phase loop

The plan's last phase is always `## Phase N — Verification`. No new code is written here, and no prior Group or phase was tested — this is the **single source of truth** for whether the plan's work is correct. It has two Groups, both validated by `Explore` (haiku) testers.

1. **Group 1 — Architecture sweep.** Dispatch one `Explore` (haiku) tester with the brief:
   - `{PLAN_FILE_PATH}`, with instruction to read the plan's **full** `## Architecture decisions` section itself (every `AD-N`, full Files affected list, directory shape, full mock snippet) — do not paste it into the prompt.
   - The list of files actually modified across all feature phases.
   - Instruction: *"For every `AD-N`, return `[FOUND] <evidence: file:line>` / `[NOT FOUND] <what was searched>` / `[UNCLEAR] <reason>`. For every Files affected row, same format. Verify directory shape matches the post-change tree. Verify code shape matches the mock code snippet — class/function names, file locations, dependency direction, public surface. Return one block on principles/patterns: `[NO VIOLATION FOUND]` or `[POSSIBLE VIOLATION: …]`."*
   - Supervisor judges: all `[FOUND]` and `[NO VIOLATION FOUND]` → pass, flip Group 1 ✅. Any `[NOT FOUND]` or `[POSSIBLE VIOLATION]` or `[UNCLEAR]` (unless the Supervisor spot-checks and clears it itself) → apply the **Verification failure rule** below. AD rules are the single source of truth and cannot be silently amended — any fix that changes an AD requires explicit user approval.

2. **Group 2 — Acceptance criteria.** After Group 1 is ✅, dispatch one `Explore` (haiku) tester with the brief:
   - `{PLAN_FILE_PATH}`, with instruction to read the plan's full `## Acceptance criteria` section itself — do not paste it into the prompt.
   - Instruction: *"For each `AC-N`, run the exact test named in its `Verify:` line (written during `Phase 1 — Write acceptance tests`) and return `[PASS] <evidence>` / `[FAIL: <evidence>]`. For criteria tagged `(manual)` (no test was written for these), return `[MANUAL CHECK REQUIRED: <reason>]` with a one-line description of what the user needs to look at."*
   - Supervisor judges:
     - All `[PASS]` (with any `[MANUAL CHECK REQUIRED]` items confirmed by the user) → flip Group 2 ✅, proceed to Finalization.
     - Any `[FAIL]` → apply the **Verification failure rule** below.
     - Any `[MANUAL CHECK REQUIRED]` → list each one to the user, ask for confirmation. Only after user confirms can Group 2 flip ✅.

### Verification failure rule

Verification is the only place a failure can occur, and it escalates on the **first** failure — there is no automatic retry and no attempt cap:

1. Stop immediately. Describe the failure to the user in plain English: which `AD-N`/`AC-N` failed, the tester's evidence, and — for a failing test — whether it looks like a bug in the implementation or a wrong/stale test from Phase 1.
2. State your best guess of the responsible Group (from earlier in the plan) and your reasoning, but don't assume it.
3. Ask the user what should happen next. Don't default to "retry" — offer it as one option alongside others: redo a specific Group (the user names it or defers to your guess), fix it themselves, amend the `AC-N`/`AD-N` (requires their explicit approval — these are the single source of truth and are never silently amended), or stop the plan here.
4. Carry out whatever the user chose — a redo is a fresh inline implementation pass through that Group's Steps 1–3, with the failure report appended as context — then re-run the full Verification phase (both Groups) fresh to confirm.
5. If it fails again, escalate again the same way — every failure gets a fresh escalation to the user, not a silent retry.

A mid-implementation architecture gap surfaced during a redo is real-time governance, not a Verification failure — see the Group loop above.

---

## Finalization step

This is **not a phase** — it has no Groups, no testers, and no rows in the plan file. It is Supervisor-only bookkeeping that marks the plan complete and propagates the result outward.

Run these in order, only after both Verification Groups are ✅:

1. **Update the GitHub issue (from-issue plans only).** If the plan title contains an issue reference (`(#N)`), post a `gh issue comment` to that issue containing:
   - Plan filename + link.
   - A checklist of every `AC-N` → `[x]` with the one-line evidence from Group 2's report.
   - Any `[MANUAL CHECK REQUIRED]` items the user confirmed, listed under "Manually verified by user".
   - Any `AD-N` additions or amendments made during execution, listed under "Architecture amendments".

   Then close the issue: run `gh issue close <N>`.
2. **Mark the matching task in `project_plan.md` (from-issue plans only).** After the issue closes, locate the row in `project_plan.md` at the repo root whose leading `#` cell equals the plan slot `N.M` (e.g., `5.6`). Flip that row's last (Status) cell from its current value to ✅. Every other byte of the file is preserved — do not rewrite the table, touch sprint goals, or alter any other row.

   **Guard:** If `project_plan.md` does not exist, or no row with a leading `#` cell matching `N.M` is found, skip the flip silently and record it in the artifacts-touched line (e.g., `project_plan.md: no row for 5.6, skipped`). The issue still closes regardless.
3. **Update `CONTEXT.md`** at the project root if it exists. Skip if it does not — do not create one.
   - Scan the completed plan for new domain terms, relationships, or vocabulary the implementation introduced (or terms whose meaning shifted). Add or revise Language / Relationships entries to match the now-shipped reality.
   - Match the file's existing style (e.g., `**Term**:` blocks with `_Avoid_:` lines, relationship bullets).
4. **Update `README.md`** at the project root only if the implementation changed something a new contributor needs to know to use or run the project (new top-level entry point, new install/run command, changed configuration surface). If the change is internal-only, skip. Do not invent README content.
5. **Output one line per artifact touched.** Examples: `Posted AC checklist to #42`, `Closed #42`, `project_plan.md: flipped 5.6 → ✅`, `project_plan.md: no row for 5.6, skipped`, `Updated CONTEXT.md: added Verification phase`, `README.md unchanged`. Then announce the plan complete.

Edit `CONTEXT.md` and `README.md` directly — same authority as plan-file edits. Issue comments use `gh issue comment`.
</content>
