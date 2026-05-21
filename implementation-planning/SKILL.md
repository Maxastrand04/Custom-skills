---
name: implementation-planning
description: Run a grill-me interview to stress-test a plan, then automatically produce a structured implementation plan file in implementation_plans/N.N_short_name.md. Use when user wants to plan a feature or task, says "let's plan", "implementation plan", or "grill me then plan".
---

# Implementation Planning

Two-phase workflow: grill the user to surface all decisions, then write the plan.

---

## Phase 1 — Grill session

### Detection order

Before any grill content runs, route the session by checking these three cases in order. Stop at the first match:

1. **Explicit `<issue-ref>` arg** — the user invoked the skill with an issue number (e.g., `42`), a full GitHub issue URL, or a natural-language description of an existing issue. Resolve natural-language descriptions against open issues via `gh issue list` / `gh issue view`. When an arg is present, jump directly to the **from-issue path** (see below) — do not run the WHAT-grill.
2. **Auto-detect (strict + confirm)** — only consider this case when **both** gates hold: (a) `new-issue` ran in the **current session** and posted an issue (you have a fresh issue URL in conversation context), AND (b) the user explicitly confirms when prompted. Even when (a) holds, **always prompt the user to confirm** before skipping the WHAT-grill — never auto-route silently. This is the strict + confirm rule: gated on a same-session `new-issue` post **and** an explicit user confirmation.
3. **Standalone fallback** — neither (1) nor (2) match. Run the full grill as today (unchanged behavior).

### From-issue path

Triggered by case (1) or a confirmed case (2) above. Behavior:

- **Skip the WHAT topics** — these are already covered by the linked issue body. Do not re-grill scope, behavior, acceptance criteria, or out-of-scope: take them as given from the issue.
- **Run the HOW topics only** — architecture, modules, files, tests, rollout. These are not in the issue body and must be resolved before writing the plan.
- **Read the issue body first.** Before starting the HOW grill, fetch the issue via `gh issue view <ref> --json title,body,labels` (or equivalent) and read it in full so the HOW questions are grounded in the issue's WHAT.

The existing standalone grill behavior (below) is unchanged — it runs only when the Detection order lands on case (3).

### Standalone grill

Interview the user relentlessly about every aspect of their plan until all decisions are resolved:

- Ask questions **one at a time**
- For each question, provide your recommended answer with brief reasoning
- Walk down each branch of the decision tree, resolving dependencies between decisions
- If a question can be answered by exploring the codebase, do that instead of asking
- Cover: scope, architecture, data model, API contracts, error handling, testing approach, rollout order, known constraints
- For each phase, ask how tasks group into Groups — **each Group is a fully independent vertical slice**: verifiable on its own, with no read-dependency on any sibling Group in the same phase. If two task bundles can't be verified independently, they belong in the same Group, or one belongs in a later phase. (See CONTEXT.md → Group.)
- For each Group, elicit the concrete test/check items the Group tester will run to confirm the Group's work **in isolation** (commands, file/symbol presence, HTTP responses, etc.). A Group-level check that requires another Group's output is a sign the Groups are wrongly split.
- For each phase, elicit integration-level test/check items that verify **all Groups in the phase compose correctly** — this is the Phase tester's job, and the only place cross-Group behavior is verified

### Final two grill steps — universal

These two steps run **regardless of which Detection-order branch you took** — they apply to **both the standalone path and the from-issue path**. Do not skip them on the from-issue path.

1. **Penultimate step — Propose plan structure with recommendation.** After every earlier topic is resolved, propose a recommended plan structure: the number of phases, the Groups per phase, and what each Group covers. **Every Group within a phase must be a fully independent vertical slice** — verifiable on its own, with no read-dependency on any sibling Group in the same phase, and no shared-file writes with any sibling Group (`supervise-implement` dispatches all Groups in a phase in parallel; a cross-Group read-dependency or a shared-file write is a plan defect — last-writer-wins races aside, two slices touching one file's different parts usually means the file is doing too much or the slices aren't really independent). Before presenting the structure, self-check each phase: *"If I dispatched all Groups in this phase in parallel right now, would any implementer (a) be blocked waiting for another's output, or (b) write to the same file as another?"* If either, merge those Groups, split the file first, or move one Group to a later phase. Include 1-2 sentences of reasoning per Group. Then **wait for user confirmation or adaptation** — iterate until the user confirms.
2. **Final step — Propose tests/checks with recommendation.** Propose:
   - Per-Group `Tests / checks` bullets that verify the Group's slice **in isolation** — no dependency on a sibling Group's output. A check that requires reading another Group's file or running a sibling's code belongs in the phase-integration block, not the Group block.
   - Per-Phase `Tests / checks (Phase N — integration)` bullets that verify **all Groups in the phase compose correctly** end-to-end. This is the only place cross-Group integration is checked; surface every cross-Group behavior here so nothing slips through.

   Include 1-2 sentences of reasoning. Then **wait for user confirmation or adaptation** — iterate until the user confirms.

Only **after both proposals are confirmed** by the user, say:

> "I think we've covered everything. Creating the implementation plan now."

Then proceed immediately to Phase 2 — do not wait for the user to prompt you.

---

## Phase 2 — Write the plan

1. **Read the template** at `~/.claude/skills/implementation-planning/template_implementation_plan.md` before writing anything.

2. **Determine plan number** — list files in `implementation_plans/` at the project root to find the next available `N.N` slot. If the directory doesn't exist, create it and start at `1.1`.

3. **Write the plan file** to `implementation_plans/N.N_short_name.md` (short_name: 2–4 words, snake_case, no articles).

4. **Follow the template exactly**:
   - Title line: `# N.N — Plan Name`
   - One-sentence summary + Goal statement
   - Status legend
   - Phase 0 — Prerequisites (external deps, blockers, decisions to confirm before coding starts)
   - Numbered phases, each with a task table: Task | File | Status
   - Claude Instructions section: Architecture, Conventions, Constraints, Order dependency, Testing

5. **Rules**:
   - Name a specific file in every task row where possible; use `—` only when genuinely unknown
   - Don't invent decisions not established in the grill session
   - The Claude Instructions section must capture all constraints and "do not" rules surfaced during grilling

6. **Phase shape**:
   - Render each Phase 1+ as N `### Group N — short name` sub-sections, each with its own task table and a `**Tests / checks (Group N):**` bullet list, followed by a final `### Tests / checks (Phase N — integration)` block.
   - Phase 0 stays a single task table with no groups and no tester block; each row is a confirmation or prerequisite the user walks through interactively.

7. Output a clickable markdown link to the new plan file as the last line of your response.
