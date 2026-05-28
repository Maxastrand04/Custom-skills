---
name: plan-build
description: Run a grill-me interview to stress-test a plan, then automatically produce a structured implementation plan file in implementation_plans/N.N_short_name.md. Use when user wants to plan a feature or task, says "let's plan", "implementation plan", or "grill me then plan".
---

# plan-build

Two-phase workflow: grill the user to surface all decisions, then write the plan.

**Tester-role scoping (binds all generated plans):**
The Group tester and Phase tester subagents check **functionality only** — that the code satisfies the `AC-N` criteria from `## Acceptance criteria` that apply to their scope. They do **not** check design, structure, or architecture. Architecture review is a separate role, owned by either an architecture-review subagent or a human reviewer named in the Group's `**Architecture tests / checks (Group N):**` block. Generated plans must reflect this split verbatim and never mix structural assertions into a functionality block.

---

## Phase 1 — Grill session

### Detection order

Before any grill content runs, route the session by checking these three cases in order. Stop at the first match:

1. **Explicit `<issue-ref>` arg** — the user invoked the skill with an issue number (e.g., `42`), a full GitHub issue URL, or a natural-language description of an existing issue. Resolve natural-language descriptions against open issues via `gh issue list` / `gh issue view`. When an arg is present, jump directly to the **from-issue path** (see below) — do not run the WHAT-grill.
2. **Auto-detect (strict + confirm)** — only consider this case when **both** gates hold: (a) `new-issue` ran in the **current session** and posted an issue (you have a fresh issue URL in conversation context), AND (b) the user explicitly confirms when prompted. Even when (a) holds, **always prompt the user to confirm** before skipping the WHAT-grill — never auto-route silently. This is the strict + confirm rule: gated on a same-session `new-issue` post **and** an explicit user confirmation.
3. **Standalone fallback** — neither (1) nor (2) match. Run the full grill as today (unchanged behavior).

### From-issue path

Triggered by case (1) or a confirmed case (2) above. Behavior:

- **Skip the WHAT topics** — these are already covered by the linked issue body. Do not re-grill scope, behavior, or out-of-scope: take them as given from the issue.
- **Lift acceptance criteria from the issue.** Parse the issue body for explicit acceptance criteria / "Done when" / checklist items; assign each one an `AC-N` ID and present the list back to the user for confirmation or edits. **Do not skip this step on the from-issue path** — `AC-N` is the contract the Verification phase tests against and must be locked before HOW questions run. If the issue has no explicit criteria, draft them from the issue body and confirm with the user.
- **Run the HOW topics only** — exploration, architecture, modules, files, tests, rollout. These are not in the issue body and must be resolved before writing the plan.
- **Read the issue body first.** Before starting the HOW grill, fetch the issue via `gh issue view <ref> --json title,body,labels` (or equivalent) and read it in full so the HOW questions are grounded in the issue's WHAT.
- **Run the Exploration step, Acceptance-criteria step, and Architecture topic block** (below) on this path too. Skipping them would make the `## Acceptance criteria` / `## Architecture decisions` sections ungrounded.
- **Capture the issue title, number, and ID tag** for use in Phase 2 — the plan filename and title must mirror the issue exactly so the link between issue and plan is obvious at a glance. The ID tag is the leading `(N)` or `(N.M)` token in the issue title (set by `new-issue`). If the issue title has no ID tag (e.g. an older issue created before this convention), tell the user and ask whether to (a) edit the issue title to add an ID, or (b) fall back to the standalone-path naming for this one plan.

The existing standalone grill behavior (below) runs in full when the Detection order lands on case (3). The Exploration step, Acceptance-criteria step, and Architecture topic block run on **both** paths.

### Exploration step (runs first, both paths)

Before asking any questions, ground the grill in what already exists. This is a hybrid checklist:

1. **Fixed project-level reads** (always, if present): `CONTEXT.md`, `docs/adr/`, top-level `README.md`, directory listing of the project root, and `implementation_plans/` for prior plans.
2. **Targeted change-specific reads**: grep/read files relevant to the change being planned — modules likely to be touched, related interfaces, neighboring code.

After exploration, emit a short **"What I found"** summary to the user covering: the relevant modules, the conventions/patterns visible in the affected area, any ADRs that constrain the change, and prior plans that touch the same code. **Wait for the user to correct misreads** before moving on — corrections at this step are cheap, downstream they propagate.

### Acceptance-criteria step (runs after Exploration, before Architecture, both paths)

`AC-N` is the contract the final Verification phase tests against. It must be locked **before** Architecture decisions are grilled — Architecture is derived from AC, not the other way around.

- **From-issue path:** lift acceptance criteria from the issue body (see From-issue path above). Assign `AC-N` IDs, present the list, confirm or edit with the user.
- **Standalone path:** drive the criteria out of the WHAT-grill. For each scope/behavior item the user named, ask: *"How would we know this is done?"* Each answer becomes one `AC-N` with a `Verify by:` clause (a concrete check — command, behavior, file/symbol presence, HTTP response, screenshot, etc.). Mark any criterion that can't be verified mechanically as `(manual)`.

Present the full `AC-N` list back to the user before moving on. **Wait for confirmation.** Iterate until the user agrees the list is the complete contract for "done."

### Standalone grill

After Exploration, interview the user relentlessly about every aspect of their plan until all decisions are resolved:

- Ask questions **one at a time**
- For each question, provide your recommended answer with brief reasoning
- Walk down each branch of the decision tree, resolving dependencies between decisions
- If a question can be answered by exploring the codebase, do that instead of asking
- **Order:** WHAT topics (scope, behavior, out-of-scope) → **Acceptance-criteria step** (see above) → **Architecture topic block** (see below) → rest of HOW (data model, API contracts, error handling, testing approach, rollout order, known constraints). On the from-issue path the WHAT topics are skipped — the order collapses to Exploration → Acceptance-criteria step → Architecture block → rest of HOW.
- For each phase, ask how tasks group into Groups — **each Group is a fully independent vertical slice**: verifiable on its own, with no read-dependency on any sibling Group in the same phase. If two task bundles can't be verified independently, they belong in the same Group, or one belongs in a later phase. (See CONTEXT.md → Group.)
- For each Group, elicit three sub-blocks: (a) **Architecture decisions (Group N)** — which `AD-N` items the Group implements and any relevant ADR references; (b) **Functionality tests / checks (Group N)** — concrete checks that verify the Group satisfies the `AC-N` criteria that fall within its scope (commands, file/symbol presence, HTTP responses, etc.) — no structural assertions; (c) **Architecture tests / checks (Group N)** — structural/conformance checks naming the runner (subagent or human reviewer). A Group-level functionality check that requires another Group's output is a sign the Groups are wrongly split.
- For each phase, elicit integration-level test/check items split into: **Functionality tests / checks (Phase N — integration)** — checks that verify the composed result satisfies the `AC-N` criteria that span multiple Groups (Phase tester's job); and **Architecture tests / checks (Phase N — integration)** — structural cross-group checks run by an architecture-review subagent or human reviewer. These are the only places cross-Group behavior and structure are verified end-to-end.

### Architecture topic block (runs on both paths, after Exploration)

The point of this block is to put the **user** in charge of structural choices so implementation phases become recipes, not goals Claude reinterprets. Decisions made here are persisted to the plan's `## Architecture decisions` section (see Phase 2 template) and bind the implementer.

**Mandatory topics** (every plan must resolve these):

- **a. Module/file placement** — where does each new piece of code live? Extend an existing module or create a new one?
- **b. Dependency direction** — what depends on what? Any new cross-layer/cross-module dependencies? Any cycles?
- **c. Boundary/interface shape** — what's the public surface of the new code (functions, types, endpoints)? What stays private?
- **d. Extend-vs-create** — for each new behavior, is there an existing function/class/module that should grow, or is a new one justified? (Anti-premature-abstraction check.)
- **g. Shared-file write conflicts** — does any Group write to the same file as another Group in the same phase? If yes, split the file first or merge the Groups.

**Conditional topics** (raise only when exploration or the mandatory topics surface a signal):

- **e. Data model touchpoints** — only if the change crosses a shared schema/type/contract.
- **Design principles** — cohesion, coupling, encapsulation, SOLID dimensions, DRY/YAGNI/KISS, composition-over-inheritance, immutability — raise the ones the change actually puts pressure on.
- **Patterns** — GoF (Strategy, Adapter, Observer, …) or architectural (layered, hexagonal/ports-and-adapters, clean, DI, event-driven, sync-vs-async boundaries) — raise when the change either follows an existing pattern in the codebase or could introduce a new one.
- **Error-handling strategy, concurrency model, testability seams, configuration boundaries, observability boundaries** — raise only when the change touches them.

**Hybrid behavior — derive, then ask:**

1. **Draft from exploration first.** Use the "What I found" summary plus the WHAT answers to draft tentative answers to the mandatory topics, and to identify which conditional topics apply. For small changes that follow existing conventions 1:1, the draft is mostly *"follows existing X in module Y"* and only needs confirmation.
2. **Ask only on ambiguity or deliberate divergence.** A targeted question looks like: *"I see Strategy pattern in `handlers/`. Should the new code follow it, or introduce something different?"* — not *"which GoF pattern do you want?"*

**Per-topic format (mandatory whenever a topic is raised):**

When you raise an architecture topic with the user, the message must contain, in order:

1. **What it is** — one-sentence definition plus a tiny concrete example of how it works.
2. **Why it exists** — what problem it solves in general.
3. **How it could help this project** — grounded in what Exploration found (cite specific files/modules/ADRs).
4. **Recommendation** — whether it's worth applying here, and why or why not.
5. **Ask the user to decide.** The recommendation is input, not the decision.

This format applies to both mandatory and conditional topics — the user must understand the topic before choosing, and the final call is theirs.

### Final four grill steps — universal

These four steps run **regardless of which Detection-order branch you took** — they apply to **both the standalone path and the from-issue path**. Do not skip them on the from-issue path.

1. **Propose `## Acceptance criteria` section with recommendation.** Draft the full `## Acceptance criteria` section (see Phase 2 template for shape): numbered `AC-N` list with one-line outcome + `Verify by:` clause per criterion, with `(manual)` tagged where mechanical verification isn't possible. From-issue plans render the issue's criteria; standalone plans render the criteria produced during the Acceptance-criteria step. Present the full draft and **wait for user confirmation or adaptation** — iterate until the user confirms. This is the contract the final Verification phase tests against.
2. **Propose `## Architecture decisions` section with recommendation.** Once `## Acceptance criteria` is confirmed, draft the full `## Architecture decisions` section (see Phase 2 template for shape): files affected, directory shape after change, each decision tagged `AD-N` with rationale and a principle/pattern/convention tag, design principles in play, patterns used/avoided, and — for any plan that adds or edits code — a **mock code snippet** that shows every architectural choice in code form (class/function shapes, file-location comments, dependency direction, public-vs-private surface, pattern wiring). Skip the mock snippet only when the plan exclusively touches non-code artifacts (e.g., `.md` files). Decisions here should be **derived from `## Acceptance criteria`** — every AD should trace back to a structural need raised by one or more `AC-N`. Present the full draft and **wait for user confirmation or adaptation** — iterate until the user confirms. This is the most load-bearing structural artifact in the plan; do not collapse it into the plan-structure step.
3. **Propose plan structure with recommendation.** Once Architecture decisions are confirmed, propose a recommended plan structure: the number of phases, the Groups per phase, and what each Group covers. **Every plan must end with a mandatory `## Phase N — Verification` phase** (see template) containing exactly two Groups — Group 1 Architecture sweep (full AD list + mock snippet vs codebase) and Group 2 Acceptance criteria (one row per `AC-N` rendered from `## Acceptance criteria`). The Verification phase writes **no new code** — it is verification only. **Every Group within a feature phase must be a fully independent vertical slice** — verifiable on its own, with no read-dependency on any sibling Group in the same phase, and no shared-file writes with any sibling Group (`plan-execute` in supervise mode dispatches all Groups in a phase in parallel; a cross-Group read-dependency or a shared-file write is a plan defect — last-writer-wins races aside, two slices touching one file's different parts usually means the file is doing too much or the slices aren't really independent). Before presenting the structure, self-check each feature phase: *"If I dispatched all Groups in this phase in parallel right now, would any implementer (a) be blocked waiting for another's output, or (b) write to the same file as another?"* If either, merge those Groups, split the file first, or move one Group to a later phase. If the plan-structure work surfaces a missing architecture decision, loop back to step 2 and update `## Architecture decisions` rather than letting the structure carry an undecided choice. If it surfaces a missing acceptance criterion, loop back to step 1. Include 1-2 sentences of reasoning per Group. Then **wait for user confirmation or adaptation** — iterate until the user confirms.
4. **Propose tests/checks with recommendation.** For each Group in a feature phase, propose three sub-blocks:
   - `**Architecture decisions (Group N):**` — which `AD-N` items the Group implements and any `ADR-NNNN` references (sits above the task table).
   - `**Functionality tests / checks (Group N):**` — concrete checks that verify this Group satisfies the `AC-N` criteria within its scope. No structural assertions; a check that requires reading another Group's file belongs in the phase-integration block instead.
   - `**Architecture tests / checks (Group N):**` — structural/conformance checks naming the runner (subagent or human reviewer) for each bullet.

   For each feature phase, also propose two integration blocks:
   - `### Functionality tests / checks (Phase N — integration)` — checks that verify the composed result satisfies the `AC-N` criteria that span multiple Groups. This is the Phase tester's only check block; surface every cross-Group AC-N here.
   - `### Architecture tests / checks (Phase N — integration)` — structural cross-group checks run by an architecture-review subagent or human reviewer.

   The Verification phase's check blocks are auto-rendered from `## Architecture decisions` (Group 1) and `## Acceptance criteria` (Group 2) — do not invent independent checks for them.

   Include 1-2 sentences of reasoning. Then **wait for user confirmation or adaptation** — iterate until the user confirms.

Only **after all four proposals are confirmed** by the user, say:

> "I think we've covered everything. Creating the implementation plan now."

Then proceed immediately to Phase 2 — do not wait for the user to prompt you.

---

## Phase 2 — Write the plan

1. **Read the template** at `~/.claude/skills/plan-build/template_implementation_plan.md` before writing anything.

2. **Determine plan number** based on the Detection-order branch:
   - **From-issue path (cases 1 and 2):** use the issue's ID tag verbatim. `(N)` → plan slot `N`; `(N.M)` → plan slot `N.M`. Do **not** pick the next free slot in `implementation_plans/` — the issue ID is authoritative. If a plan file with that slot already exists, stop and ask the user how to resolve (overwrite, rename existing, etc.) rather than silently picking a different slot.
   - **Standalone path (case 3):** list files in `implementation_plans/` at the project root to find the next available `N.N` slot. If the directory doesn't exist, create it and start at `1.1`.

3. **Write the plan file** to `implementation_plans/<slot>_short_name.md`. Derive `short_name` based on the Detection-order branch:
   - **From-issue path (cases 1 and 2):** `short_name` is **1–3 words, snake_case, no articles** — just enough to skim a directory listing. The ID tag already identifies which issue the plan tackles, so the slug does not need to mirror the full issue title. Pick the most load-bearing nouns/verbs from the issue title; drop the ID tag, the `[feature]` / `[bug]` prefix, and any filler. Example: issue `(1.3) [feature] Add OAuth login for admin dashboard` → `1.3_oauth_login.md`. Example: issue `(2.1) [feature] skill: generate test structure from codebase + docs` → `2.1_test_structure.md`.
   - **Standalone path (case 3):** `short_name` is 2–4 words, snake_case, no articles.

4. **Follow the template exactly**:
   - Title line: `# <slot> — Plan Name` — on the from-issue path, `Plan Name` is the **verbatim issue title with the ID tag stripped** (keep the `[feature]` / `[bug]` prefix and original casing/punctuation) followed by ` (#<issue-number>)`. Example: `# 1.3 — [feature] Add OAuth login for admin dashboard (#42)`. On the standalone path, use a short human-readable title derived from the grill.
   - One-sentence summary + Goal statement
   - Status legend
   - **`## Acceptance criteria` section** (sits **above `## Architecture decisions`**) — populated from the confirmed AC proposal. Numbered `AC-N` list with one-line outcome + `Verify by:` clause per criterion, with `(manual)` tags where mechanical verification isn't possible. This is the contract the Verification phase tests against.
   - **`## Architecture decisions` section** (sits **above Phase 0**, below `## Acceptance criteria`) — populated from the confirmed Architecture proposal. Includes files affected, directory shape after change, each decision tagged `AD-N` with rationale and a principle/pattern/convention tag, design principles in play, patterns used/avoided, and a **mock code snippet** that sketches every architectural choice in code form (class/function shapes, file locations, dependency direction, pattern wiring). The mock snippet is **required for any plan that adds or edits code**; skip it only when the plan exclusively touches non-code artifacts (e.g., `.md` files, prose). This section is the user's structural contract with the implementer.
   - Phase 0 — Prerequisites (external deps, blockers, decisions to confirm before coding starts)
   - Numbered feature phases, each with a task table: Task | File | Status. Where a task implements or depends on a specific architecture decision, cite it inline with `(per AD-N)`.
   - **`## Phase N — Verification`** as the mandatory final phase. No new code; Group 1 is the Architecture sweep (full `AD-N` list + mock snippet vs codebase), Group 2 is the Acceptance criteria check (one row per `AC-N`, rendered from `## Acceptance criteria`). Render the Group 2 task table and check block by listing each `AC-N` verbatim — the `Verify by:` clause is the check.
   - Claude Instructions section: Architecture binding, Conventions, Constraints, Order dependency, Testing.

5. **Rules**:
   - Name a specific file in every task row where possible; use `—` only when genuinely unknown
   - Don't invent decisions not established in the grill session
   - The Claude Instructions section must capture all constraints and "do not" rules surfaced during grilling
   - The Claude Instructions section must include an `**Architecture binding:**` rule: *"Do not introduce structural choices (new modules, new patterns, new dependency directions, new cross-layer dependencies) not covered by `## Architecture decisions`. If a task requires one, stop and surface it to the user before writing code — never improvise structure."*

6. **Phase shape**:
   - Render each Phase 1+ as N `### Group N — short name` sub-sections. Each Group sub-section contains, in order: (1) a one-line description, (2) `**Architecture decisions (Group N):**` sub-block listing the `AD-N` items the Group implements and any `ADR-NNNN` references (sits above the task table), (3) the task table, (4) `**Functionality tests / checks (Group N):**` bullet list — checks that verify this Group satisfies the `AC-N` criteria within its scope; no structural assertions, (5) `**Architecture tests / checks (Group N):**` bullet list (structural/conformance checks, each bullet names the runner as `(subagent)` or `(human)`). After all Group sub-sections, render two integration blocks: `### Functionality tests / checks (Phase N — integration)` (checks that verify `AC-N` criteria spanning multiple Groups) and `### Architecture tests / checks (Phase N — integration)` (structural cross-group checks naming the runner).
   - Phase 0 stays a single task table with no groups and no tester block; each row is a confirmation or prerequisite the user walks through interactively.

7. Output a clickable markdown link to the new plan file as the last line of your response.
