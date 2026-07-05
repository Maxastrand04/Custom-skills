---
name: implementation-plan-execute
description: Drive an implementation plan to completion in one of two modes — hands-on (model
  implements inline, user owns architecture review per Group) or supervise (parallel claude
  implementer subagents per Group, Architecture tester subagent owns architecture review).
  Use when user says "implementation-plan-execute", "supervise", "implement the plan", "run the implementation
  plan", "drive the plan group by group", "serial plan execution", or invokes /implementation-plan-execute.
---

# implementation-plan-execute

You drive an implementation plan to completion in one of two modes: **hands-on** (you implement inline, the user reviews architecture per Group) or **supervise** (parallel `claude` implementer subagents per Group, a separate Architecture-tester subagent reviews architecture).

See `CONTEXT.md` at the repo root for canonical definitions of Group, Group tester, Phase tester, Hands-on mode, Supervise mode, Tester brief, Implementer brief, and Mode trigger.

**Point, don't paste.** Every subagent dispatch (implementer, Group tester, Architecture tester, Phase tester) gets the plan file's path and a scope label, and reads its own sections from the plan file directly — never a pasted copy of `## Acceptance criteria`, `## Architecture decisions`, or a `Tests / checks` block inside the dispatch prompt. Pasted blocks repeat verbatim across every Group and every retry, and that repetition lives in the Supervisor's own context, not the subagent's — the single largest avoidable driver of context growth over a multi-phase run. The Supervisor's job is dispatch and judgment, not restating plan content it already wrote to disk.

**Terse verdicts only.** After judging a Group, Phase, or retry, state the one-line verdict (e.g. "Group 2: ✅ pass", "Group 3: FAIL — retry 1/3, <one-line reason>") and move on. Do not re-paste a tester's report, do not re-summarize a prior phase, do not restate plan content the plan file already holds. The plan file's checkboxes are the sole source of truth for cross-phase state — reason from them, not from scrollback.

---

## Input

Parse the user's invocation message for:

1. **Mode token** — `hands-on` or `supervise` (any position in the message). If absent or unrecognized, defer to **Mode selection** below.
2. **Plan reference** — `plan N.N` (any position). If absent, list `implementation_plans/` and pick the file with the highest `N.N` prefix.
3. Confirm the chosen plan with the user before doing anything else.

**Six supported invocation forms:**

| Form | Mode token | Plan arg | Behaviour |
|------|-----------|----------|-----------|
| `/implementation-plan-execute hands-on plan 4.2` | `hands-on` | `plan 4.2` | Lock hands-on; use `4.2_*.md`; confirm |
| `/implementation-plan-execute supervise plan 4.2` | `supervise` | `plan 4.2` | Lock supervise; use `4.2_*.md`; confirm |
| `/implementation-plan-execute hands-on` | `hands-on` | absent | Lock hands-on; auto-pick highest `N.N`; confirm |
| `/implementation-plan-execute supervise` | `supervise` | absent | Lock supervise; auto-pick highest `N.N`; confirm |
| `/implementation-plan-execute plan 4.2` | absent | `plan 4.2` | Use `4.2_*.md`; confirm; then ask mode |
| `/implementation-plan-execute` | absent | absent | Auto-pick highest `N.N`; confirm; then ask mode |

If the mode token is absent or unknown after parsing, do **not** guess — fall through to **Mode selection**.

---

## Mode selection

If the invocation message contained `hands-on` or `supervise`, lock that mode silently and skip this section.

Otherwise, ask the user: **"Run this hands-on (model implements inline, you review architecture per Group) or supervised (parallel implementer subagents, Architecture tester reviews architecture)?"** Wait for explicit choice before proceeding.

---

## Plan precondition check

After confirming the plan and mode, grep the chosen plan for `**Architecture decisions (Group N):**` inside every `### Group N` block under feature phases.

If any Group block is missing this sub-heading, fail loud and halt:

> This plan was generated before per-group architecture sections were required. Re-plan with `/implementation-planning`.

This check applies identically to both modes — do not skip it.

---

## Bootstrap exploration sweep

Shared by both modes. After the plan precondition check and before Phase 0, dispatch **one `Explore` subagent (haiku)** to summarize the current state of the files the plan touches. Neither the Supervisor nor any dispatched implementer reads the source itself just to get oriented — this offloads discovery so working context stays focused on dispatch, judgment, and (in hands-on mode) the actual edits.

- **Brief:** *"Read the files listed in `## Architecture decisions` → Files affected. For each file, return: current shape (top-level classes/functions, public surface), where it lives in the directory tree, any obvious patterns or conventions in use. Do not read CONTEXT.md or unrelated files. Return a structured summary, one section per file."*
- **Model:** `haiku`.
- Write the returned summary to `{EXPLORATION_SUMMARY_PATH}` (a scratch file, e.g. `implementation_plans/.exploration-summary_N.N.md` next to the plan) — never into the plan file, and never quoted back into the Supervisor's own response. In supervise mode, each implementer brief points the implementer at this path (scoped to the files that Group touches); in hands-on mode, the Supervisor reads its own scoped slice directly before stating architecture (Step 1). Either way, the contents are never pasted into a prompt or a response.
- **Refresh per phase:** at the start of each feature phase **after Phase 1**, re-dispatch the same `Explore` brief but scoped to only the files modified during the immediately preceding phase. Overwrite the matching entries in the file — do not re-read the whole file back into context to do this, just replace the named sections.
- **Skip refresh on the Verification phase** — Verification writes no new code, so the prior summary is still accurate.
- **Delete `{EXPLORATION_SUMMARY_PATH}`** during Finalization — it is scratch, not a plan artifact.

---

## Phase 0 — Interactive prerequisites

Phase 0 is **never** delegated to a tester. Walk it row-by-row with the user, grill-me style:

- For each Phase 0 row, restate the task in plain English and ask the user to confirm, decide, or supply the missing information.
- If a row requires a quick code check (e.g., "confirm no existing directory"), you may dispatch a `claude` subagent to gather the fact and report back, but the row only flips ✅ after the user confirms.
- You (the Supervisor) may edit the plan file directly to record decisions made during this walkthrough (e.g., a chosen value, a confirmed assumption).
- Flip the row ⬜ → ✅ on user confirmation. Phase 0 is the **only** place ✅ is set without a tester pass.

When every Phase 0 row is ✅, announce "Phase 0 complete — starting Phase 1" and proceed.

---

## Hands-on mode

**Architecture review is the user's role in this mode.** Neither the model nor any dispatched subagent reviews architecture. Functionality testers verify behavior only — they never check design, structure, or architecture.

**Context discipline (hands-on).** This mode has no per-Group subagent boundary for implementation — every Read/Edit you do to write the code happens in the Supervisor's own thread, for every Group, across the whole plan, in one continuous conversation. That's the mode's defining tradeoff (real-time architecture review needs the model that's about to write code in the room) and it cannot be delegated away, but don't pile incidental waste on top of it:
- The **bootstrap exploration sweep** (run once before Phase 0, refreshed per phase — see above) already wrote the **Exploration summary file**. Use it to state architecture in Step 1 — do not Read whole files just to describe their current shape.
- When implementing (Step 3), read only the exact region you're about to change (grep to locate, then targeted `Read` with `offset`/`limit`) rather than whole files, unless the file is already short.
- Don't paste implemented code or diffs back into your own response — the `Edit`/`Write` call is the record. Name the files touched in one line and move on (per **Terse verdicts**).

For each feature phase, in order:

  For each Group in the phase, in order:

  **Step 1 — State architecture (per AD-7)**

  state architecture — read the Group's `**Architecture decisions (Group N):**` sub-block from the plan. Tell the user which AD-N items this Group follows and how the upcoming code will follow them. Wait for explicit user approval before writing any code.

  **Step 2 — Architecture rejection loop**

  If the user rejects the architecture statement, revise it and re-propose. Continue until the user gives explicit approval. No implementation step is reachable until the user approves.

  **Step 3 — Inline implementation (no claude implementer subagent dispatch) (per AC-8)**

  On approval: flip every task row in this Group ⬜ → 🟡 in the plan file. Implement the Group's changes inline in the main thread. Do NOT dispatch a `claude` implementer subagent for any task in this Group.

  **Step 4 — Group tester dispatch (per AC-9, AD-2)**

  Read `tester-brief.md`. Substitute:
  - `{PLAN_FILE_PATH}` → the plan file's path
  - `{SCOPE_TAG}` → `"Phase N, Group M"` (the current phase and group numbers)

  Dispatch one `Explore` (haiku) subagent with the substituted brief. The tester reads its own checks block from the plan file — do not paste it into the prompt.

  **Step 5 — Group tester result (per AC-10, AC-11, AD-8)**

  On `Status: PASS`: flip 🟡 → ✅ for this Group. A Group advances only after both architecture approval (Step 2) and a group tester pass (this step).

  On `Status: FAIL`: judge bug-vs-bad-test using the `Failing checks` + `Failure site` + `Output excerpt` from the tester's report. Fix the issue. Retry once (re-read `tester-brief.md`, substitute, re-dispatch).

  On second `Status: FAIL` (2 attempts exhausted): **stop and escalate to the user** — surface the `Status: FAIL` block from the tester verbatim, including the failing test name and reason. Do not continue.

  Retry budget for Group tester: **2 attempts total** (1 initial + 1 retry). This is distinct from supervise mode's 3-attempt budget.

  After the last Group in the phase is ✅:

  **Step 6 — Phase tester dispatch (per AC-12, AD-2)**

  Read `tester-brief.md`. Substitute:
  - `{PLAN_FILE_PATH}` → the plan file's path
  - `{SCOPE_TAG}` → `"Phase N — integration"`

  Dispatch one `Explore` (haiku) subagent with the substituted brief. The tester reads its own checks block from the plan file — do not paste it into the prompt.

  **Step 7 — Phase tester result (per AC-13, AC-14, AD-8)**

  On `Status: PASS` on the first attempt: proceed to the next phase.

  On `Status: PASS` on the second attempt (retry): **notify the user** — "Code changed during retry; architecture may need a re-check." Then proceed.

  On `Status: FAIL`: judge bug-vs-bad-test using the tester's report. Fix the issue. Retry once.

  On second `Status: FAIL` (2 attempts exhausted): **stop and escalate to the user** — surface the `Status: FAIL` block verbatim. Do not continue.

  Retry budget for Phase tester: **2 attempts total** (1 initial + 1 retry) — same as Group tester.

---

## Supervise mode

### Per-feature-phase loop

For each feature phase, in order:

**1. Dispatch every Group in the phase in parallel:**

- Flip every task row in every Group from ⬜ → 🟡 in the plan file in one edit (do not interleave with dispatch).
- In a single response, emit one `Agent` call per Group dispatching a `claude` implementer. Each implementer's prompt is `implementer-brief.md` with placeholders substituted:
  - `{PLAN_FILE_PATH}` ← the plan file's path
  - `{GROUP_LABEL}` ← `"Phase N, Group M"`
  - `{EXPLORATION_SUMMARY_PATH}` ← the scratch file from the bootstrap sweep

  The implementer reads its own AC/AD/task-table/checks sections from the plan file and its own scoped slice of the exploration summary from disk — none of that text is pasted into the dispatch prompt.
- As each implementer reports done, dispatch **two `Explore` (haiku) testers in parallel for that Group**: the Group tester (functionality) and the Architecture tester (structure). The Supervisor judges both reports.
- For each Group: when both reports return, judge them per the tester contracts below. On combined pass, flip rows 🟡 → ✅. On any failure, apply the retry rule for that Group only; other Groups are unaffected.
- Wait until every Group is ✅ before running the Phase tester.

**2. After every Group in the phase is ✅:**

- Read `tester-brief.md`. Substitute:
  - `{PLAN_FILE_PATH}` → the plan file's path
  - `{SCOPE_TAG}` → `"Phase N — integration"`
- Dispatch one `Explore` (haiku) Phase tester with the substituted brief. The tester reads its own checks block from the plan file. Supervisor judges per tester contracts.
- On Supervisor-judged pass, proceed to the next phase.
- On Supervisor-judged failure, apply the **Phase tester failure rule** below.

### Tester report contracts

**Group tester brief (functionality — per tester-brief.md):**

Read `tester-brief.md`. Substitute:
- `{PLAN_FILE_PATH}` → the plan file's path
- `{SCOPE_TAG}` → `"Phase N, Group M"`

Dispatch one `Explore` (haiku) per Group. The tester reads its own checks block from the plan file (functionality checks only — not architecture checks) and returns `Status: PASS` or `Status: FAIL` + failing checks per the PASS/FAIL contract in `tester-brief.md`. The Supervisor judges: PASS → proceed; FAIL → apply retry rule.

**Architecture tester brief (per Group, parallel with Group tester):**

Dispatch one `Explore` (haiku) per Group with this inline brief:
- `{PLAN_FILE_PATH}` and `{GROUP_LABEL}` (`"Phase N, Group M"`). Instruct it to read, from the plan file itself, only the `AD-N` items and "Files affected" rows that this Group's tasks cite via `(per AD-N)` annotations, plus the relevant subset of the mock code snippet — not the whole plan.
- Instruction: *"Return one line per AD-N: `[FOUND] <evidence>` / `[NOT FOUND] <what was searched>` / `[UNCLEAR] <reason>`. Return one line per 'Files affected' row in scope: same format. Return one block on principles/patterns: `[NO VIOLATION FOUND]` or `[POSSIBLE VIOLATION: <principle/pattern> — <evidence>]`."*

**Supervisor judgment:**
- All `[FOUND]` → pass.
- Any `[NOT FOUND]` → fail.
- Any `[UNCLEAR]` → Supervisor either spot-checks the file itself or treats as fail.
- `[POSSIBLE VIOLATION]` → **never silently accept.** Stop, report to user with the tester's evidence and a Supervisor recommendation: *"amend AD-N to allow this"* or *"this will be fixed by Group X in Phase Y"* or *"this is a real violation, retry"*. **AD rules are the single source of truth and cannot be amended without explicit user approval.**

### [ARCH GAP] escape hatch

If an implementer returns `[ARCH GAP] <description> | Recommendation: <…>` instead of completing its tasks:

1. The Supervisor halts that Group (no tester dispatch).
2. Surfaces the gap to the user in plain English, including the implementer's recommendation.
3. Waits for the user to either (a) approve an AD addition/amendment — the Supervisor edits the plan's `## Architecture decisions` section to add `AD-N+1` or amend an existing AD verbatim per the user's words; or (b) reject and ask the user to redesign.
4. Re-dispatches the Group fresh with the updated plan.
5. **This does not consume a retry attempt.** Correct escalation is not a failure.

### Parallelism rule + plan-defect escalation

**Within a phase, every Group runs in parallel. Always.** Dispatch all of the phase's implementers in a single response containing one `Agent` call per Group. There is no per-phase serial path — by definition (see CONTEXT.md → Group) a Group is a fully independent vertical slice.

Group testers also run in parallel — they are read-only `Explore` agents.

**If you spot a read-dependency or shared-file write between sibling Groups in the same phase, halt and escalate to the user as a plan defect.** Do not serialize as a workaround. State the violating Group pair and the specific dependency; ask the user to either merge them into one Group or move one to a later phase. Resume only after the plan is fixed. The plan file is the artifact to fix — not the dispatch strategy.

### Status-flip rule

- **Supervisor flips ⬜ → 🟡** when dispatching the implementer for that Group.
- **Supervisor flips 🟡 → ✅** **only** after the Group tester (or Phase tester) reports pass. The tester's pass is what authorises the flip; the Supervisor performs the edit.
- The Supervisor is forbidden from flipping a row to ✅ directly without a tester pass.
- **Exception:** Phase 0 rows flip ✅ on user confirmation, not tester pass.

### Retry rule (Group level)

A Group gets **3 total attempts**: 1 initial implementation + 2 retries on tester failure. Group tester and Architecture tester share this budget — a failure of either (or both) counts as one attempt. This is distinct from hands-on mode's 2-attempt budget.

On any tester failure, dispatch a **fresh** `claude` implementer for that Group. The retry brief contains:

- The original implementer brief (per `implementer-brief.md` with substituted placeholders).
- **Both** the Group tester report and the Architecture tester report — even the one that passed.
- A **one-line Supervisor framing** above the reports, written by the Supervisor in plain English, e.g., *"Behavior failed at X, structure was correct — fix only the behavior, do not move files."*

After the third failure (3 attempts exhausted), **stop and escalate to the user**. Do not silently continue. An `[ARCH GAP]` return does **not** consume a retry attempt.

### Phase tester failure rule

When the Phase tester reports failure:

1. Do **not** auto-re-dispatch. First, describe the failure to the user in plain English: phase number, which Group(s) are implicated, which task(s), the tester's reason.
2. State your best guess of the responsible Group and your reasoning.
3. Ask the user to either **name** the responsible Group or **defer** to your guess.
4. Re-dispatch the chosen Group's implementer (a fresh `claude` subagent, with the Phase tester's failure report appended as context), then re-run that Group's tester, then re-run the Phase tester.
5. **3-attempt cap at the phase level** — counted independently of Group-level attempts. After 3 Phase tester failures, escalate to the user.

---

## Verification phase loop

The plan's last phase is always `## Phase N — Verification`. No new code is written here. It has two Groups, both validated by `Explore` (haiku) testers, no implementer dispatches.

1. **Group 1 — Architecture sweep.** Dispatch one `Explore` (haiku) tester with the brief:
   - `{PLAN_FILE_PATH}`, with instruction to read the plan's **full** `## Architecture decisions` section itself (every `AD-N`, full Files affected list, directory shape, full mock snippet) — do not paste it into the prompt.
   - The list of files actually modified across all feature phases.
   - Instruction: *"For every `AD-N`, return `[FOUND] <evidence: file:line>` / `[NOT FOUND] <what was searched>` / `[UNCLEAR] <reason>`. For every Files affected row, same format. Verify directory shape matches the post-change tree. Verify code shape matches the mock code snippet — class/function names, file locations, dependency direction, public surface. Return one block on principles/patterns: `[NO VIOLATION FOUND]` or `[POSSIBLE VIOLATION: …]`."*
   - Supervisor judges per **Tester report contract**. On combined pass, flip Group 1 ✅. On any `[NOT FOUND]` or `[POSSIBLE VIOLATION]`, **do not retry automatically** — escalate to user with the report and a Supervisor recommendation: *amend an AD (requires explicit user approval), open a follow-up, or fix now*. AD rules are the single source of truth; do not silently amend.

2. **Group 2 — Acceptance criteria.** After Group 1 is ✅, dispatch one `Explore` (haiku) tester with the brief:
   - `{PLAN_FILE_PATH}`, with instruction to read the plan's full `## Acceptance criteria` section itself — do not paste it into the prompt.
   - Instruction: *"For each `AC-N`, run the `Verify by:` check and return `[PASS] <evidence>` / `[FAIL: <evidence>]` / `[MANUAL CHECK REQUIRED: <reason>]`. Do not skip criteria tagged `(manual)` — return `[MANUAL CHECK REQUIRED]` for those by default with a one-line description of what the user needs to look at."*
   - Supervisor judges:
     - All `[PASS]` (with any `[MANUAL CHECK REQUIRED]` items confirmed by the user) → flip Group 2 ✅, proceed to Finalization.
     - Any `[FAIL]` → escalate to user with the failure report + Supervisor recommendation (amend AC with user approval, open follow-up, fix now). Do not auto-retry.
     - Any `[MANUAL CHECK REQUIRED]` → list each one to the user, ask for confirmation. Only after user confirms can Group 2 flip ✅.

3. **Phase tester (Verification):** dispatch one `Explore` (haiku) Phase tester to confirm all `AD-N` are `[FOUND]`, all `AC-N` are `[PASS]` or user-confirmed-manual, and no `[POSSIBLE VIOLATION]` is outstanding. On Supervisor-judged pass, proceed to Finalization.

---

## Finalization step

This is **not a phase** — it has no Groups, no testers, and no rows in the plan file. It is Supervisor-only bookkeeping that marks the plan complete and propagates the result outward.

Run these in order, only after the Verification phase Phase tester passes:

1. **Update the GitHub issue (from-issue plans only).** If the plan title contains an issue reference (`(#N)`), post a `gh issue comment` to that issue containing:
   - Plan filename + link.
   - A checklist of every `AC-N` → `[x]` with the one-line evidence from Group 2's report.
   - Any `[MANUAL CHECK REQUIRED]` items the user confirmed, listed under "Manually verified by user".
   - Any `AD-N` additions or amendments made via the `[ARCH GAP]` escape hatch during execution, listed under "Architecture amendments".

   Then close the issue: run `gh issue close <N>`.
2. **Mark the matching task in `project_plan.md` (from-issue plans only).** After the issue closes, locate the row in `project_plan.md` at the repo root whose leading `#` cell equals the plan slot `N.M` (e.g., `5.6`). Flip that row's last (Status) cell from its current value to ✅. Every other byte of the file is preserved — do not rewrite the table, touch sprint goals, or alter any other row.

   **Guard:** If `project_plan.md` does not exist, or no row with a leading `#` cell matching `N.M` is found, skip the flip silently and record it in the artifacts-touched line (e.g., `project_plan.md: no row for 5.6, skipped`). The issue still closes regardless.
3. **Update `CONTEXT.md`** at the project root if it exists. Skip if it does not — do not create one.
   - Scan the completed plan for new domain terms, relationships, or vocabulary the implementation introduced (or terms whose meaning shifted). Add or revise Language / Relationships entries to match the now-shipped reality.
   - Match the file's existing style (e.g., `**Term**:` blocks with `_Avoid_:` lines, relationship bullets).
4. **Update `README.md`** at the project root only if the implementation changed something a new contributor needs to know to use or run the project (new top-level entry point, new install/run command, changed configuration surface). If the change is internal-only, skip. Do not invent README content.
5. **Output one line per artifact touched.** Examples: `Posted AC checklist to #42`, `Closed #42`, `project_plan.md: flipped 5.6 → ✅`, `project_plan.md: no row for 5.6, skipped`, `Updated CONTEXT.md: added Verification phase, Architecture tester`, `README.md unchanged`. Then announce the plan complete.

The Supervisor edits `CONTEXT.md` and `README.md` directly — same authority as plan-file edits. Issue comments use `gh issue comment`.
