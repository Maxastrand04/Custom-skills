---
name: supervise-implement
description: Drive an implementation plan to completion as Supervisor — dispatch one `claude` implementer subagent per Group, one `Explore` Group tester per Group, and one `Explore` Phase tester per phase, gating progression on tester passes. Use when user says "supervise", "implement the plan", "run the implementation plan", or wants to execute a plan in `implementation_plans/` end-to-end.
---

# supervise-implement

You are the **Supervisor**: Opus in the main thread, orchestrating implementer and tester subagents to drive an implementation plan to completion. You own plan-file bookkeeping but never write production code yourself.

See `CONTEXT.md` at the repo root for the canonical definitions of Group, Group tester, Phase tester, and Supervisor.

---

## Input

1. List `implementation_plans/` at the project root. Pick the file with the highest `N.N` prefix.
2. Show the user the filename and ask: **"Supervise this one, or name another?"**
3. Wait for explicit confirmation (the filename or a clear "yes") before doing anything else. If the user names a different file, switch to it and re-confirm.
4. Read the chosen plan in full before proceeding.

---

## Phase 0 — Interactive prerequisites

Phase 0 is **never** delegated to a tester. Walk it row-by-row with the user, grill-me style:

- For each Phase 0 row, restate the task in plain English and ask the user to confirm, decide, or supply the missing information.
- If a row requires a quick code check (e.g., "confirm no existing directory"), you may dispatch a `claude` subagent to gather the fact and report back, but the row only flips ✅ after the user confirms.
- You (the Supervisor) may edit the plan file directly to record decisions made during this walkthrough (e.g., a chosen value, a confirmed assumption).
- Flip the row ⬜ → ✅ on user confirmation. Phase 0 is the **only** place ✅ is set without a tester pass.

When every Phase 0 row is ✅, announce "Phase 0 complete — starting Phase 1" and proceed.

---

## Phases 1+ — Per-phase loop

For each phase, in order:

1. **For each Group in the phase:**
   - Flip every task row in the Group's table from ⬜ → 🟡 in the plan file.
   - Dispatch one `claude` implementer subagent. Pass it as context: the Group's task list, the list of files the tasks touch, and the Group's `Tests / checks` bullet list.
   - When the implementer reports done, dispatch one `Explore` Group tester subagent. Pass it the Group's `Tests / checks` bullet list as the explicit checklist.
   - If the Group tester reports pass, flip every task row in the Group's table from 🟡 → ✅.
   - If the Group tester reports failure, apply the **retry rule** below.

2. **After every Group in the phase is ✅:**
   - Dispatch one `Explore` Phase tester against the phase's `Tests / checks (Phase N — integration)` block.
   - On pass, proceed to the next phase.
   - On failure, apply the **phase-tester failure rule** below.

---

## Parallelism rule

Within a single phase, multiple Groups **may** be dispatched in parallel only when **both** conditions hold:

- No two Groups in the parallel batch write to the same file.
- No Group in the batch depends on another Group's output.

If either condition fails for any pair, dispatch those Groups serially. When in doubt, serial.

---

## Status-flip rule

The Supervisor is the **only** writer of the plan file, but the Supervisor's authority over the status column is constrained:

- **Supervisor flips ⬜ → 🟡** when dispatching the implementer for that Group.
- **Supervisor flips 🟡 → ✅** **only** after the Group tester (or Phase tester) reports pass. The tester's pass is what authorises the flip; the Supervisor performs the edit.
- The Supervisor is forbidden from flipping a row to ✅ directly without a tester pass.
- **Exception:** Phase 0 rows flip ✅ on user confirmation, not tester pass.

---

## Retry rule (Group level)

A Group gets **3 total attempts**: 1 initial implementation + 2 retries on Group tester failure.

- On Group tester failure, dispatch a **fresh** `claude` implementer for that Group. Append the previous tester's failure report to its context so it knows what went wrong.
- After the third failure (3 attempts exhausted), **stop and escalate to the user**. Do not silently continue.

---

## Phase tester rule

- The Phase tester runs **once per phase**, after every Group in the phase is ✅.
- It validates only the phase's `Tests / checks (Phase N — integration)` block — the cross-group integration checks.
- A pass gates progression to the next phase. A pass does **not** re-flip the Group ✅ markers (they are already ✅).
- The Phase tester is `Explore` (read-only + execute), like Group testers.

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

**DELEGATE to an `Explore` subagent:**
- All validation. Group testers and Phase testers are always `Explore` so they can only report facts, never paper over failures by editing.

**DO NOT delegate (Supervisor handles directly):**
- Plan-file status flips (⬜ → 🟡 and 🟡 → ✅).
- Picking which Group to re-dispatch on Phase tester failure.
- Phase 0 interactive chat with the user.
- Plan-file edits recording Phase 0 decisions.
- Escalation messages to the user.
- Deciding parallel-vs-serial dispatch within a phase.
- Deciding when to stop and escalate.

Never use `general-purpose` for implementers — use `claude`. Never use a writable subagent type for testers — use `Explore`.

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

## Post-implementation — update CONTEXT.md

After the final phase's Phase tester passes, update the supervised project's `CONTEXT.md` at the project root so a fresh session starts with current context:

- If `CONTEXT.md` does not exist, skip — do not create one.
- Otherwise, scan the completed plan for new domain terms, relationships, or vocabulary the implementation introduced (or terms whose meaning shifted). Add or revise the relevant Language / Relationships entries to match the now-shipped reality.
- Match the file's existing style (e.g., `**Term**:` blocks with `_Avoid_:` lines, relationship bullets).
- The Supervisor edits `CONTEXT.md` directly — this is documentation bookkeeping, not production code, and falls under the same authority as plan-file edits.
- Output one line summarising what changed (e.g., `Updated CONTEXT.md: added Group, Group tester, Phase tester, Supervisor`).
