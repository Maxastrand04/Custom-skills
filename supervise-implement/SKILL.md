---
name: supervise-implement
description: Drive an implementation plan to completion as Supervisor — dispatch one `claude` implementer subagent per Group, one `Explore` Group tester per Group, and one `Explore` Phase tester per phase, gating progression on tester passes. Use when user says "supervise", "implement the plan", "run the implementation plan", or wants to execute a plan in `implementation_plans/` end-to-end.
---

# supervise-implement

You are the **Supervisor**: Opus in the main thread, orchestrating implementer and tester subagents to drive an implementation plan to completion. You own plan-file bookkeeping but never write production code yourself.

See `CONTEXT.md` at the repo root for the canonical definitions of Group, Group tester, Phase tester, and Supervisor.

---

## Input

The Supervisor starts with **no context other than this skill and the project root**. Everything else is built by reading the plan and dispatching subagents — never assume prior conversation context.

1. List `implementation_plans/` at the project root. Pick the file with the highest `N.N` prefix.
2. Show the user the filename and ask: **"Supervise this one, or name another?"**
3. Wait for explicit confirmation (the filename or a clear "yes") before doing anything else. If the user names a different file, switch to it and re-confirm.
4. Read the chosen plan in full before proceeding.

---

## Bootstrap exploration sweep

After reading the plan and before Phase 0, dispatch **one `Explore` subagent (haiku)** to summarize the current state of the files the plan touches. The Supervisor does not read the source itself — it offloads discovery so its working context stays focused on dispatch and judgment.

- **Brief:** *"Read the files listed in `## Architecture decisions` → Files affected. For each file, return: current shape (top-level classes/functions, public surface), where it lives in the directory tree, any obvious patterns or conventions in use. Do not read CONTEXT.md or unrelated files. Return a structured summary, one section per file."*
- **Model:** `haiku`.
- The returned summary is held **in memory only** — never written to disk or into the plan file. It is included in every implementer brief (scoped to the files that Group touches).
- **Refresh per phase:** at the start of each feature phase **after Phase 1**, re-dispatch the same `Explore` brief but scoped to only the files modified during the immediately preceding phase. Replace the matching entries in the in-memory summary.
- **Skip refresh on the Verification phase** — Verification writes no new code, so the prior summary is still accurate.

---

## Phase 0 — Interactive prerequisites

Phase 0 is **never** delegated to a tester. Walk it row-by-row with the user, grill-me style:

- For each Phase 0 row, restate the task in plain English and ask the user to confirm, decide, or supply the missing information.
- If a row requires a quick code check (e.g., "confirm no existing directory"), you may dispatch a `claude` subagent to gather the fact and report back, but the row only flips ✅ after the user confirms.
- You (the Supervisor) may edit the plan file directly to record decisions made during this walkthrough (e.g., a chosen value, a confirmed assumption).
- Flip the row ⬜ → ✅ on user confirmation. Phase 0 is the **only** place ✅ is set without a tester pass.

When every Phase 0 row is ✅, announce "Phase 0 complete — starting Phase 1" and proceed.

---

## Phases 1+ — Per-feature-phase loop

This loop applies to every feature phase (Phase 1 through Phase N-1). The final phase (`## Phase N — Verification`) has its own loop, below.

For each feature phase, in order:

1. **Dispatch every Group in the phase in parallel:**
   - Flip every task row in every Group from ⬜ → 🟡 in the plan file in one edit (do not interleave with dispatch).
   - In a single response, emit one `Agent` call per Group dispatching a `claude` implementer. Implementer brief contents are defined in **Implementer brief contract** below.
   - As each implementer reports done, dispatch **two `Explore` (haiku) testers in parallel for that Group**: the Group tester (behavior) and the Architecture tester (structure). Both return structured checklists, not pass/fail — the Supervisor judges them.
   - For each Group: when both reports return, the Supervisor judges them per **Tester report contract** below. On combined pass, flip rows 🟡 → ✅. On any failure, apply the retry rule for that Group only; other Groups are unaffected.
   - Wait until every Group is ✅ before running the Phase tester.

2. **After every Group in the phase is ✅:**
   - Dispatch one `Explore` (haiku) Phase tester against the phase's `Tests / checks (Phase N — integration)` block. Same reporter-style contract: structured checklist, Supervisor judges.
   - On Supervisor-judged pass, proceed to the next phase.
   - On Supervisor-judged failure, apply the **phase-tester failure rule** below.

---

## Implementer brief contract

Every `claude` implementer dispatch contains exactly the following, and nothing else:

1. **Architecture binding preamble (verbatim from the plan's Claude Instructions section):** *"Do not introduce structural choices (new modules, new patterns, new dependency directions, new cross-layer dependencies) not covered by `## Architecture decisions`. If a task requires one, stop and surface it to the user before writing code — never improvise structure. Cite the relevant `AD-N` when a task implements a decision."*
2. The plan's full `## Acceptance criteria` section.
3. The plan's full `## Architecture decisions` section (including the mock code snippet, if present).
4. This Group's task table + file list + `Tests / checks (Group N):` block.
5. The plan's `## Claude Instructions` section.
6. The scoped exploration-summary entries — only the entries for files this Group touches.
7. Hard rule (verbatim): *"Read only files named in your task table, file list, or exploration summary. Do not read CONTEXT.md, other plans, or unrelated source. If you hit a structural choice not covered by `## Architecture decisions`, stop and return `[ARCH GAP] <description> | Recommendation: <new AD wording or AD-N amendment>` — do not improvise structure."*

Nothing else: no prior-phase narrative, no Supervisor commentary, no other Groups' briefs.

---

## Tester report contract

Group testers, Architecture testers, and the Phase tester are all `Explore` (haiku) subagents. They report findings; the **Supervisor judges**.

**Group tester brief:**
- Receives the Group's `Tests / checks (Group N):` bullets verbatim.
- Returns one line per bullet: `[FOUND] <evidence: file:line or command output excerpt>` / `[NOT FOUND] <what was searched>` / `[UNCLEAR] <reason>`.

**Architecture tester brief (per Group, parallel with Group tester):**
- Receives the AD-N items and "Files affected" rows that this Group's tasks cite via `(per AD-N)` annotations — scoped to this Group, not the whole plan. Also receives the relevant subset of the mock code snippet.
- Returns one line per AD-N: `[FOUND] <evidence>` / `[NOT FOUND] <what was searched>` / `[UNCLEAR] <reason>`.
- Returns one line per "Files affected" row in scope: same format.
- Returns one block on principles/patterns: `[NO VIOLATION FOUND]` or `[POSSIBLE VIOLATION: <principle/pattern> — <evidence>]`.

**Phase tester brief:**
- Receives only the `Tests / checks (Phase N — integration)` bullets verbatim.
- Returns one line per bullet, same `[FOUND]`/`[NOT FOUND]`/`[UNCLEAR]` format.

**Supervisor judgment:**
- All `[FOUND]` → pass.
- Any `[NOT FOUND]` → fail.
- Any `[UNCLEAR]` → Supervisor either spot-checks the file itself or treats as fail.
- `[POSSIBLE VIOLATION]` → **never silently accept.** Stop, report to user with the tester's evidence and a Supervisor recommendation: *"amend AD-N to allow this"* or *"this will be fixed by Group X in Phase Y"* or *"this is a real violation, retry"*. **AD rules are the single source of truth and cannot be amended without explicit user approval.**

---

## [ARCH GAP] escape hatch

If an implementer returns `[ARCH GAP] <description> | Recommendation: <…>` instead of completing its tasks:

1. The Supervisor halts that Group (no tester dispatch).
2. Surfaces the gap to the user in plain English, including the implementer's recommendation.
3. Waits for the user to either (a) approve an AD addition/amendment — the Supervisor edits the plan's `## Architecture decisions` section to add `AD-N+1` or amend an existing AD verbatim per the user's words; or (b) reject and ask the user to redesign.
4. Re-dispatches the Group fresh with the updated plan.
5. **This does not consume a retry attempt.** Correct escalation is not a failure.

---

## Parallelism rule

**Within a phase, every Group runs in parallel. Always.** Dispatch all of the phase's implementers in a single response containing one `Agent` call per Group. There is no per-phase serial path — by definition (see CONTEXT.md → Group) a Group is a fully independent vertical slice. If two bundles can't be verified independently, the planner should have made them one Group or split them across phases.

Group testers also run in parallel — they are read-only `Explore` agents.

**If you spot a read-dependency or shared-file write between sibling Groups in the same phase, halt and escalate to the user as a plan defect.** Do not serialize as a workaround. State the violating Group pair and the specific dependency; ask the user to either merge them into one Group or move one to a later phase. Resume only after the plan is fixed. The plan file is the artifact to fix — not the dispatch strategy.

Cross-Group integration is the Phase tester's job, not the Supervisor's dispatch choice. Trust it.

---

## Status-flip rule

The Supervisor is the **only** writer of the plan file, but the Supervisor's authority over the status column is constrained:

- **Supervisor flips ⬜ → 🟡** when dispatching the implementer for that Group.
- **Supervisor flips 🟡 → ✅** **only** after the Group tester (or Phase tester) reports pass. The tester's pass is what authorises the flip; the Supervisor performs the edit.
- The Supervisor is forbidden from flipping a row to ✅ directly without a tester pass.
- **Exception:** Phase 0 rows flip ✅ on user confirmation, not tester pass.

---

## Retry rule (Group level)

A Group gets **3 total attempts**: 1 initial implementation + 2 retries on tester failure. Group tester and Architecture tester share this budget — a failure of either (or both) counts as one attempt.

On any tester failure, dispatch a **fresh** `claude` implementer for that Group. The retry brief contains:

- The original implementer brief (per **Implementer brief contract**).
- **Both** the Group tester report and the Architecture tester report — even the one that passed. The implementer needs to know what's already correct so it doesn't break it on retry.
- A **one-line Supervisor framing** above the reports, written by the Supervisor in plain English, e.g., *"Behavior failed at X, structure was correct — fix only the behavior, do not move files."* This forces the Supervisor to scope the retry before dispatching.

After the third failure (3 attempts exhausted), **stop and escalate to the user**. Do not silently continue. An `[ARCH GAP]` return does **not** consume a retry attempt — see [ARCH GAP] escape hatch.

---

## Phase tester rule

- The Phase tester runs **once per feature phase**, after every Group in the phase is ✅.
- It validates only the phase's `Tests / checks (Phase N — integration)` block — the cross-group integration checks.
- A Supervisor-judged pass gates progression to the next phase. A pass does **not** re-flip the Group ✅ markers (they are already ✅).
- The Phase tester is `Explore` (haiku), reporter-style — Supervisor judges per **Tester report contract**.

---

## Phase tester failure rule

When the Phase tester reports failure:

1. Do **not** auto-re-dispatch. First, describe the failure to the user in plain English:
   - Phase number
   - Which Group(s) are implicated
   - Which task(s) within those Groups
   - The tester's reason for the failure
2. State your **best guess** of the responsible Group and your reasoning.
3. Ask the user to either **name** the responsible Group or **defer** to your guess.
4. Re-dispatch the chosen Group's implementer (a fresh `claude` subagent, with the Phase tester's failure report appended as context), then re-run that Group's tester, then re-run the Phase tester.
5. **3-attempt cap at the phase level** — counted independently of Group-level attempts. After 3 Phase tester failures, escalate to the user.

---

## Delegation rules

**DELEGATE to a `claude` subagent:**
- Writing or editing production code for a Group's task list.

**DELEGATE to an `Explore` subagent (always pinned to `haiku`):**
- The bootstrap exploration sweep and per-phase exploration refreshes.
- All validation: Group testers, Architecture testers, Phase testers, and the Verification phase's per-Group testers. All are reporter-style — they return structured checklists, the Supervisor judges.

**DO NOT delegate (Supervisor handles directly):**
- Plan-file status flips (⬜ → 🟡 and 🟡 → ✅).
- **Judging tester reports.** Testers report findings; the Supervisor decides pass/fail.
- Picking which Group to re-dispatch on Phase tester failure.
- Writing the one-line retry framing above the appended tester reports.
- Phase 0 interactive chat with the user.
- Plan-file edits recording Phase 0 decisions or `[ARCH GAP]` AD amendments.
- Escalation messages to the user (including plan-defect escalations when Groups violate the vertical-slice invariant, `[POSSIBLE VIOLATION]` reports, `[FAIL]` AC results, and `[ARCH GAP]` escape-hatch returns).
- Deciding when to stop and escalate.
- The Finalization step (issue comment, CONTEXT.md, README.md).

Never use `general-purpose` for implementers — use `claude`. Never use a writable subagent type for testers — use `Explore`. Always pin testers and exploration agents to `haiku` via the Agent tool's `model` parameter.

---

## Reporting cadence

**On success, be quiet.** One line per phase boundary:

- `Starting Phase N — [phase name]` when entering a phase.
- `Phase N complete.` when the Phase tester passes.

**On any tester failure or escalation, output:**

- Phase number
- Group name
- Task description
- Plain-English reason for the failure
- What you're about to do next (retry, re-dispatch, ask user)

No other narration. The user reads the plan file for detail.

---

## Verification phase loop (mandatory final phase)

The plan's last phase is always `## Phase N — Verification`. No new code is written here. It has two Groups, both validated by `Explore` (haiku) testers, no implementer dispatches.

1. **Group 1 — Architecture sweep.** Dispatch one `Explore` (haiku) tester with the brief:
   - The plan's **full** `## Architecture decisions` section (every `AD-N`, full Files affected list, directory shape, full mock snippet).
   - The list of files actually modified across all feature phases.
   - Instruction: *"For every `AD-N`, return `[FOUND] <evidence: file:line>` / `[NOT FOUND] <what was searched>` / `[UNCLEAR] <reason>`. For every Files affected row, same format. Verify directory shape matches the post-change tree. Verify code shape matches the mock code snippet — class/function names, file locations, dependency direction, public surface. Return one block on principles/patterns: `[NO VIOLATION FOUND]` or `[POSSIBLE VIOLATION: …]`."*
   - Supervisor judges per **Tester report contract**. On combined pass, flip Group 1 ✅. On any `[NOT FOUND]` or `[POSSIBLE VIOLATION]`, **do not retry automatically** — escalate to user with the report and a Supervisor recommendation: *amend an AD (requires explicit user approval), open a follow-up, or fix now*. AD rules are the single source of truth; do not silently amend.

2. **Group 2 — Acceptance criteria.** After Group 1 is ✅, dispatch one `Explore` (haiku) tester with the brief:
   - The plan's full `## Acceptance criteria` section.
   - Instruction: *"For each `AC-N`, run the `Verify by:` check and return `[PASS] <evidence>` / `[FAIL: <evidence>]` / `[MANUAL CHECK REQUIRED: <reason>]`. Do not skip criteria tagged `(manual)` — return `[MANUAL CHECK REQUIRED]` for those by default with a one-line description of what the user needs to look at."*
   - Supervisor judges:
     - All `[PASS]` (with any `[MANUAL CHECK REQUIRED]` items confirmed by the user) → flip Group 2 ✅, proceed to Finalization.
     - Any `[FAIL]` → escalate to user with the failure report + Supervisor recommendation (amend AC with user approval, open follow-up, fix now). Do not auto-retry.
     - Any `[MANUAL CHECK REQUIRED]` → list each one to the user, ask for confirmation. Only after user confirms can Group 2 flip ✅.

3. **Phase tester (Verification):** dispatch one `Explore` (haiku) Phase tester to confirm all `AD-N` are `[FOUND]`, all `AC-N` are `[PASS]` or user-confirmed-manual, and no `[POSSIBLE VIOLATION]` is outstanding. On Supervisor-judged pass, proceed to Finalization.

---

## Finalization step (after Verification passes)

This is **not a phase** — it has no Groups, no testers, and no rows in the plan file. It is Supervisor-only bookkeeping that marks the plan complete and propagates the result outward.

Run these in order, only after the Verification phase Phase tester passes:

1. **Update the GitHub issue (from-issue plans only).** If the plan title contains an issue reference (`(#N)`), post a `gh issue comment` to that issue containing:
   - Plan filename + link.
   - A checklist of every `AC-N` → `[x]` with the one-line evidence from Group 2's report.
   - Any `[MANUAL CHECK REQUIRED]` items the user confirmed, listed under "Manually verified by user".
   - Any `AD-N` additions or amendments made via the `[ARCH GAP]` escape hatch during execution, listed under "Architecture amendments".
   - **Never close the issue.** Closing is the user's call.
2. **Update `CONTEXT.md`** at the project root if it exists. Skip if it does not — do not create one.
   - Scan the completed plan for new domain terms, relationships, or vocabulary the implementation introduced (or terms whose meaning shifted). Add or revise Language / Relationships entries to match the now-shipped reality.
   - Match the file's existing style (e.g., `**Term**:` blocks with `_Avoid_:` lines, relationship bullets).
3. **Update `README.md`** at the project root only if the implementation changed something a new contributor needs to know to use or run the project (new top-level entry point, new install/run command, changed configuration surface). If the change is internal-only, skip. Do not invent README content.
4. **Output one line per artifact touched.** Examples: `Posted AC checklist to #42`, `Updated CONTEXT.md: added Verification phase, Architecture tester`, `README.md unchanged`. Then announce the plan complete.

The Supervisor edits `CONTEXT.md` and `README.md` directly — same authority as plan-file edits. Issue comments use `gh issue comment`.
