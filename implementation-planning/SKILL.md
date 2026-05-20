---
name: implementation-planning
description: Run a grill-me interview to stress-test a plan, then automatically produce a structured implementation plan file in implementation_plans/N.N_short_name.md. Use when user wants to plan a feature or task, says "let's plan", "implementation plan", or "grill me then plan".
---

# Implementation Planning

Two-phase workflow: grill the user to surface all decisions, then write the plan.

---

## Phase 1 — Grill session

Interview the user relentlessly about every aspect of their plan until all decisions are resolved:

- Ask questions **one at a time**
- For each question, provide your recommended answer with brief reasoning
- Walk down each branch of the decision tree, resolving dependencies between decisions
- If a question can be answered by exploring the codebase, do that instead of asking
- Cover: scope, architecture, data model, API contracts, error handling, testing approach, rollout order, known constraints
- For each phase, ask how tasks group into agent-bundles — bundle when tasks share a file or form one atomic change; split otherwise
- For each group, elicit the concrete test/check items the tester will run to confirm the group's work (commands, file/symbol presence, HTTP responses, etc.)
- For each phase, elicit integration-level test/check items that cross group boundaries

When you have resolved all open questions, say:

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
