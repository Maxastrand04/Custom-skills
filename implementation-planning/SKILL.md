---
name: implementation-planning
description: Run a grill-me interview to stress-test a plan, then automatically produce a structured implementation plan file in implementation_plans/N.N_short_name.md. Use when user wants to plan a feature or task, says "let's plan", "implementation plan", or "grill me then plan".
---

# implementation-planning

Two-phase workflow: grill the user to reach shared understanding, then write the whole plan in one pass.

**Group blocks (binds all generated plans, single source of truth):**
Every Group in a feature phase carries one block, and no other wording for it is authoritative — everywhere else in this skill that mentions it is pointing back here:

- `**Architecture decisions (Group N):**` — which `AD-N` items the Group implements, plus any `ADR-NNNN` references.

Groups and phases carry **no** functionality or architecture test blocks — testing is not interleaved between phases. Every plan is test-driven at the phase level: `## Phase 1 — Write acceptance tests` (always second, right after Phase 0) writes the failing (red) automated tests that encode every non-`(manual)` `AC-N`, before any implementation exists. Implementation phases (`Phase 2` through the second-to-last phase) then make those tests pass. The mandatory `Phase N — Verification` (see Phase 2 template, always last) is the **single source of truth for testing**: it runs once, after every implementation phase is done, sweeping the full `AD-N` list against the codebase (Group 1) and running the Phase-1 tests to confirm every `AC-N` now passes green (Group 2). On any failure, the Supervisor escalates to the user immediately — no automatic retry, and the user decides what happens next (see `implementation-plan-execute`'s Verification failure rule).

---

## Phase 1 — Grill session

You are a developer grilling a project leader about code and product structure. Every question asked anywhere in this phase — WHAT topics, HOW topics, Architecture topics — runs under the `grilling` skill's interview mechanics: invoke it. This skill supplies *what* to ask and in what order; `grilling` supplies *how* (one question at a time, your recommendation first, explore before asking, walk each branch to resolution). Don't restate those mechanics inline elsewhere in this phase.

The whole phase runs as **one continuous session toward a single reached understanding** — not a sequence of stop-and-confirm checkpoints. You draft as you go and only present work back to the user when there's something genuinely open to resolve; you don't pause after every section to get a formal sign-off. There is exactly one confirmation gate, at the end (see Final grill steps below), covering the whole draft at once.

### Detection order

Before any grill content runs, route the session by checking these three cases in order. Stop at the first match:

1. **Explicit `<issue-ref>` arg** — the user invoked the skill with an issue number (e.g., `42`), a full GitHub issue URL, or a natural-language description of an existing issue. Resolve natural-language descriptions against open issues via `gh issue list` / `gh issue view`. When an arg is present, jump directly to the **from-issue path** (see below) — do not run the WHAT-grill.
2. **Auto-detect (strict + confirm)** — only consider this case when **both** gates hold: (a) `new-issue` ran in the **current session** and posted an issue (you have a fresh issue URL in conversation context), AND (b) the user explicitly confirms when prompted. Even when (a) holds, **always prompt the user to confirm** before skipping the WHAT-grill — never auto-route silently. This is the strict + confirm rule: gated on a same-session `new-issue` post **and** an explicit user confirmation.
3. **Standalone fallback** — neither (1) nor (2) match. Run the full grill as today (unchanged behavior).

### From-issue path

Triggered by case (1) or a confirmed case (2) above. Behavior:

- **Skip the WHAT topics** — these are already covered by the linked issue body. Do not re-grill scope, behavior, or out-of-scope: take them as given from the issue.
- **Lift acceptance criteria from the issue.** Parse the issue body for explicit acceptance criteria / "Done when" / checklist items; assign each one an `AC-N` ID. These feed into the combined draft at the end (see Final grill steps) — don't stop for a separate confirmation here.
- **Run the HOW topics only** — exploration, architecture, modules, files, rollout. These are not in the issue body and must be resolved before writing the plan.
- **Read the issue body first.** Before starting the HOW grill, fetch the issue via `gh issue view <ref> --json title,body,labels` (or equivalent) and read it in full so the HOW questions are grounded in the issue's WHAT.
- **Run the Exploration step and Architecture topic block** (below) on this path too. Skipping them would make the `## Acceptance criteria` / `## Architecture decisions` sections ungrounded.
- **Capture the issue title, number, and ID tag** for use in Phase 2 — the plan filename and title must mirror the issue exactly so the link between issue and plan is obvious at a glance. The ID tag is the leading `(N)` or `(N.M)` token in the issue title (set by `new-issue`). If the issue title has no ID tag (e.g. an older issue created before this convention), tell the user and ask whether to (a) edit the issue title to add an ID, or (b) fall back to the standalone-path naming for this one plan.

The existing standalone grill behavior (below) runs in full when the Detection order lands on case (3). The Exploration step and Architecture topic block run on **both** paths.

### Exploration step (runs first, both paths)

Before asking any questions, ground the grill in what already exists. This is a hybrid checklist:

1. **Fixed project-level reads** (always, if present): `CONTEXT.md`, `docs/adr/`, top-level `README.md`, directory listing of the project root, and `implementation_plans/` for prior plans.
2. **Targeted change-specific reads**: grep/read files relevant to the change being planned — modules likely to be touched, related interfaces, neighboring code.

After exploration, emit a short **"What I found"** summary to the user covering: the relevant modules, the conventions/patterns visible in the affected area, any ADRs that constrain the change, and prior plans that touch the same code. **Wait for the user to correct misreads** before moving on — corrections at this step are cheap, downstream they propagate.

### Standalone grill

After Exploration, work through every remaining decision (see `grilling` invocation note above):

- **Order:** WHAT topics (scope, behavior, out-of-scope) → acceptance criteria (drive out of the WHAT-grill: for each scope/behavior item, ask *"How would we know this is done?"*) → **Architecture topic block** (below) → rest of HOW (data model, API contracts, error handling, rollout order, known constraints). On the from-issue path the WHAT topics are skipped — the order collapses to Exploration → Architecture block → rest of HOW.
- For each phase, ask how tasks group into Groups — **each Group is a fully independent vertical slice**: verifiable on its own, with no read-dependency on any sibling Group in the same phase. If two task bundles can't be verified independently, they belong in the same Group, or one belongs in a later phase. (See CONTEXT.md → Group.)
- For each Group, elicit which `AD-N` items it implements (see **Group blocks** above).

### Architecture topic block (runs on both paths, after Exploration)

The point of this block is to put the **user** in charge of structural choices so implementation phases become recipes, not goals Claude reinterprets. Decisions made here are persisted to the plan's `## Architecture decisions` section (see Phase 2 template) and bind the implementer.

Use judgment on what's worth raising for *this* change — there's no fixed checklist. The usual suspects: module/file placement, dependency direction, public interface shape, extend-vs-create (is there an existing piece that should grow instead of a new one?), shared-file write conflicts across Groups, data model touchpoints, design principles under pressure, patterns followed or introduced, error-handling/concurrency/testability/config/observability boundaries. Raise the ones the change actually puts pressure on; skip the rest silently rather than asking about them just to rule them out.

Draft from Exploration first — for a change that follows existing convention 1:1, most topics collapse to a one-line *"follows existing X in module Y, confirm?"*. Go deeper only where the choice is genuinely ambiguous or you're proposing a deliberate divergence: say what the option is, why it might apply here (grounded in what Exploration found), and your recommendation — then let the user decide. The recommendation is input, not the decision.

### Final grill steps — universal

These steps run **regardless of which Detection-order branch you took** — they apply to **both the standalone path and the from-issue path**. Do not skip them on the from-issue path.

1. **Draft the whole plan content in one continuous pass, without a separate stop-and-confirm after each piece.** Cover, in this order, using your own recommendation to keep momentum (still a `grilling` session underneath — recommendation first, explore before asking — but aimed at one shared understanding, not a checkpoint per section):
   - `## Acceptance criteria`: numbered `AC-N` list, terse — outcome + verify clause, sacrifice grammar for brevity. The verify clause should name the concrete automated test that will prove it (e.g. `AC-1: login redirects to dashboard. Verify: tests/test_login.py::test_admin_redirect.`) — that exact test gets written in `Phase 1 — Write acceptance tests` and re-run in Verification. Tag `(manual)` only when no automated test is possible; those get a plain-English check instead of a test path. From-issue plans render the issue's lifted criteria; standalone plans render what the WHAT-grill produced.
   - `## Architecture decisions`: files affected, directory shape after change, `AD-N` list — terse, same style as AC (decision + why + principle/pattern/convention tag) — design principles in play, patterns used/avoided, and — for any plan that adds or edits code — a **mock code snippet** showing every architectural choice in code form (class/function shapes, file-location comments, dependency direction, public-vs-private surface, pattern wiring). Skip the mock snippet only when the plan exclusively touches non-code artifacts. Every AD should trace back to a structural need raised by one or more `AC-N`.
   - **Plan structure**, test-driven and fixed at three anchor positions:
     - `## Phase 0 — Prerequisites` (unchanged, interactive walkthrough, no Groups).
     - `## Phase 1 — Write acceptance tests` (mandatory, always second): one or more Groups that write the actual failing (red) automated tests named in each non-`(manual)` `AC-N`'s verify clause, using the project's existing test framework/conventions (from Exploration). No implementation code is written here — the tests should fail because the behavior doesn't exist yet, not because of a broken test. Skip this phase's content (leave it a stub noting "no automatable criteria") only if every `AC-N` is `(manual)`.
     - `Phase 2` through the second-to-last phase: implementation Groups that make the Phase-1 tests pass.
     - `## Phase N — Verification` (mandatory, always last, see template) with exactly two Groups — Group 1 Architecture sweep (full AD list + mock snippet vs codebase) and Group 2 Acceptance criteria (re-runs each Phase-1 test and confirms it now passes, plus confirms any `(manual)` criteria with the user). The Verification phase writes **no new code**.
     - **Every Group within any phase (including Phase 1) must be a fully independent vertical slice** — verifiable on its own, with no read-dependency on any sibling Group in the same phase, and no shared-file writes with any sibling Group. A cross-Group read-dependency or shared-file write is a plan defect: it means the Groups aren't really separate work, and `implementation-plan-execute` can't state one Group's architecture and verify its correctness without pulling in another's half-finished change. Self-check each phase: *"Could I implement and verify this Group on its own, without anything from a sibling Group in the same phase?"* If not, merge those Groups, split the file first, or move one Group to a later phase.
   - **Branch**: which git branch the implementer should work from — a new branch (default: named after the plan slot/slug) or an existing one the user names.
   If drafting any of these surfaces a gap in an earlier piece (a missing AD, a missing AC), fix it inline rather than treating the pieces as locked in sequence — this is one draft, not four.
2. **Present the complete combined draft once** — Acceptance criteria, Architecture decisions, plan structure with Groups, and Branch — together, with 1-2 sentences of reasoning per Group. **Wait for the user to confirm or correct the whole thing.** Iterate on the combined draft together until the user agrees it's the full contract for "done" — don't re-split this back into separate per-section stops.

Only **after the combined draft is confirmed**, say:

> "I think we've covered everything. Creating the implementation plan now."

Then proceed immediately to Phase 2 — do not wait for the user to prompt you.

---

## Phase 2 — Write the plan

1. **Read the template** at `~/.claude/skills/implementation-planning/template_implementation_plan.md` before writing anything.

2. **Determine plan number** based on the Detection-order branch:
   - **From-issue path (cases 1 and 2):** use the issue's ID tag verbatim. `(N)` → plan slot `N`; `(N.M)` → plan slot `N.M`. Do **not** pick the next free slot in `implementation_plans/` — the issue ID is authoritative. If a plan file with that slot already exists, stop and ask the user how to resolve (overwrite, rename existing, etc.) rather than silently picking a different slot.
   - **Standalone path (case 3):** list files in `implementation_plans/` at the project root to find the next available `N.N` slot. If the directory doesn't exist, create it and start at `1.1`.

3. **Write the plan file** to `implementation_plans/<slot>_short_name.md`. Derive `short_name` based on the Detection-order branch:
   - **From-issue path (cases 1 and 2):** `short_name` is **1–3 words, snake_case, no articles** — just enough to skim a directory listing. The ID tag already identifies which issue the plan tackles, so the slug does not need to mirror the full issue title. Pick the most load-bearing nouns/verbs from the issue title; drop the ID tag, the `[feature]` / `[bug]` prefix, and any filler. Example: issue `(1.3) [feature] Add OAuth login for admin dashboard` → `1.3_oauth_login.md`. Example: issue `(2.1) [feature] skill: generate test structure from codebase + docs` → `2.1_test_structure.md`.
   - **Standalone path (case 3):** `short_name` is 2–4 words, snake_case, no articles.

4. **Follow the template exactly** for section shape, order, and content — it was already read in step 1. Populate `## Acceptance criteria` and `## Architecture decisions` from the confirmed combined draft; populate `**Branch:**` from the confirmed branch decision; don't invent content beyond what Phase 1 confirmed. Keep `AC-N` and `AD-N` entries terse — sacrifice grammar for brevity, one line each, no restating the same point twice. The one thing the template can't tell you — the title line derivation:
   - Title line: `# <slot> — Plan Name`. From-issue path: `Plan Name` is the **verbatim issue title with the ID tag stripped** (keep the `[feature]` / `[bug]` prefix and original casing/punctuation) followed by ` (#<issue-number>)`. Example: `# 1.3 — [feature] Add OAuth login for admin dashboard (#42)`. Standalone path: a short human-readable title derived from the grill.

5. **Rules**:
   - Name a specific file in every task row where possible; use `—` only when genuinely unknown
   - Don't invent decisions not established in the grill session
   - The Claude Instructions section must capture all constraints and "do not" rules surfaced during grilling
   - The Claude Instructions section must include an `**Architecture binding:**` rule: *"Do not introduce structural choices (new modules, new patterns, new dependency directions, new cross-layer dependencies) not covered by `## Architecture decisions`. If a task requires one, stop and surface it to the user before writing code — never improvise structure."*
   - No Group or Phase (other than the final `Phase N — Verification`) carries a test/check block — testing is not interleaved. Note this in Claude Instructions under **Testing**: nothing is verified until the final Verification phase, and that phase re-runs the tests written in `Phase 1 — Write acceptance tests` rather than inventing new checks.

6. **Phase shape**: `Phase 1` onward renders as `### Group N — short name` sub-sections (description, then the `**Architecture decisions (Group N):**` line from **Group blocks** above, then the task table) — see the template for the exact rendering. No functionality/architecture test blocks per Group or per phase-integration. Phase 0 stays a single task table with no groups; each row is a confirmation or prerequisite the user walks through interactively. `Phase 1 — Write acceptance tests` is always second and always present, even if trivial. `Phase N — Verification` keeps its own two-Group shape (Architecture sweep, Acceptance criteria) exactly as in the template — that's the one place tests actually run.

7. Output a clickable markdown link to the new plan file as the last line of your response.
</content>
