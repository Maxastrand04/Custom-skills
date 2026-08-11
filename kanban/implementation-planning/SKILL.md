---
name: implementation-planning
description: Run a grill-me interview to stress-test a plan, then automatically produce a structured implementation plan file in implementation_plans/N.N_short_name.md. Use when user wants to plan a feature or task, says "let's plan", "implementation plan", or "grill me then plan".
---

# implementation-planning

Two-phase workflow: grill the user to reach shared understanding, then write the whole plan in one pass.

**Groups carry no architecture block (binds all generated plans):**
Architecture and coding rules are project-wide — one enforceable rule per `ADR-NNNN` in `docs/adr/` (authored by `codebase-rules`), not decided plan-by-plan. A plan names the rule-ADRs it operates under in a single `## Rules in play` section (see Phase 2 template) and otherwise leaves *how* the code is written to the implementer; the separate code-review session enforces the rule-ADRs against the committed diff. If planning surfaces a structural choice no rule covers and the choice is project-wide (it would recur beyond this plan), don't bake a one-off decision into the plan — hand it to `codebase-rules` to become a rule-ADR. A Group therefore carries only its description and task table.

Groups and phases carry **no** functionality or architecture test blocks — testing is not interleaved between phases. Every plan is test-driven at the phase level: `## Phase 1 — Red` (always second, right after Phase 0) writes the failing (red) automated tests that encode every non-`(manual)` `AC-N`, before any implementation exists. The Green phases (`Phase 2` through the second-to-last) then make those tests pass. The mandatory `Phase N — Verification` (see Phase 2 template, always last) is the **single source of truth for "does it work"**: it runs once, after every implementation phase is done, re-running the Phase-1 tests to confirm every `AC-N` now passes green. It does **not** check architecture — a separate code-review session enforces the rule-ADRs against the committed diff. On any failure, the Supervisor escalates to the user immediately — no automatic retry, and the user decides what happens next (see `implementation-plan-execute`'s Verification failure rule).

---

## Phase 1 — Grill session

You are a developer grilling a project leader about code and product structure. Every question asked anywhere in this phase — WHAT topics, HOW topics, Rules-in-play — runs under the `grilling` skill's interview mechanics: invoke it. This skill supplies *what* to ask and in what order; `grilling` supplies *how* (one question at a time, your recommendation first, explore before asking, walk each branch to resolution). Don't restate those mechanics inline elsewhere in this phase.

The whole phase runs as **one continuous session toward a single reached understanding** — not a sequence of stop-and-confirm checkpoints. You draft as you go and only present work back to the user when there's something genuinely open to resolve; you don't pause after every section to get a formal sign-off. There is exactly one confirmation gate, at the end (see Final grill steps below), covering the whole draft at once.

### Detection order

Before any grill content runs, route the session by checking these three cases in order. Stop at the first match:

1. **Explicit `<issue-ref>` arg** — the user invoked the skill with the **GitHub issue number** (`42` or `#42`), a full GitHub issue URL, or a natural-language description of an existing issue. The GitHub number is the canonical way in; resolve URLs and natural-language descriptions down to it via `gh issue list` / `gh issue view`. When an arg is present, jump directly to the **from-issue path** (see below) — do not run the WHAT-grill.
2. **Auto-detect (strict + confirm)** — only consider this case when **both** gates hold: (a) `new-issue` ran in the **current session** and posted an issue (you have a fresh issue URL in conversation context), AND (b) the user explicitly confirms when prompted. Even when (a) holds, **always prompt the user to confirm** before skipping the WHAT-grill — never auto-route silently. This is the strict + confirm rule: gated on a same-session `new-issue` post **and** an explicit user confirmation.
3. **Standalone fallback** — neither (1) nor (2) match. Run the full grill as today (unchanged behavior).

### From-issue path

Triggered by case (1) or a confirmed case (2) above. Behavior:

- **Skip the WHAT topics** — these are already covered by the linked issue body. Do not re-grill scope, behavior, or out-of-scope: take them as given from the issue.
- **Lift acceptance criteria from the issue.** Parse the issue body for explicit acceptance criteria / "Done when" / checklist items; assign each one an `AC-N` ID. These feed into the combined draft at the end (see Final grill steps) — don't stop for a separate confirmation here.
- **Run the HOW topics only** — exploration, architecture, modules, files, rollout. These are not in the issue body and must be resolved before writing the plan.
- **Read the issue body first.** Before starting the HOW grill, fetch the issue via `gh issue view <ref> --json title,body,labels` (or equivalent) and read it in full so the HOW questions are grounded in the issue's WHAT.
- **Run the Exploration step and Rules-in-play block** (below) on this path too. Skipping them would make the `## Acceptance criteria` / `## Rules in play` sections ungrounded.
- **Capture the issue title and number, and derive the plan slot** for use in Phase 2 — the plan filename and title must mirror the issue so the link between issue and plan is obvious at a glance. Two title conventions are both valid, and the slot follows whichever the issue uses:
  - **Tagged** — the title leads with an `(N)` or `(N.M)` token (`sprint-planning` tickets). Slot = that token verbatim: `(1.3) [feature] …` → slot `1.3`.
  - **Untagged** — no leading token (`new-issue` issues). Slot = the GitHub issue number: `#42` → slot `42`.

  Never ask the user to retitle an issue to fit a convention.

- **Capture the branch slug** from the issue body's `## Branch` section. The implementing branch is `<issue-number>-<slug>` — the issue chose the slug, this skill supplies the number.

The existing standalone grill behavior (below) runs in full when the Detection order lands on case (3). The Exploration step and Rules-in-play block run on **both** paths.

### Exploration step (runs first, both paths)

Before asking any questions, ground the grill in what already exists. This is a hybrid checklist:

1. **Fixed project-level reads** (always, if present): `CONTEXT.md`, top-level `README.md`, directory listing of the project root, and `implementation_plans/` for prior plans. Plus `docs/adr/`: list it and read every file's title, `**Rule:**`, `**Scope:**`, and `**Status:**` lines. A file carrying a `**Rule:**` line is a **rule-ADR** — binding and citable; one without it is a classic decision-ADR — context only, never listed in `## Rules in play`. If `docs/adr/` doesn't exist, the project has no rule set: say so and recommend running `codebase-rules` before planning.
2. **Targeted change-specific reads**: grep/read files relevant to the change being planned — modules likely to be touched, related interfaces, neighboring code.

After exploration, emit a short **"What I found"** summary to the user covering: the relevant modules, the conventions/patterns visible in the affected area, any ADRs that constrain the change, and prior plans that touch the same code. **Wait for the user to correct misreads** before moving on — corrections at this step are cheap, downstream they propagate.

### Standalone grill

After Exploration, work through every remaining decision (see `grilling` invocation note above):

- **Order:** WHAT topics (scope, behavior, out-of-scope) → acceptance criteria (drive out of the WHAT-grill: for each scope/behavior item, ask *"How would we know this is done?"*) → **Rules-in-play block** (below) → rest of HOW (data model, API contracts, error handling, rollout order, known constraints). On the from-issue path the WHAT topics are skipped — the order collapses to Exploration → Rules-in-play block → rest of HOW.
- For each phase, ask how tasks group into Groups — **each Group is a fully independent vertical slice**: verifiable on its own, with no read-dependency on any sibling Group in the same phase. If two task bundles can't be verified independently, they belong in the same Group, or one belongs in a later phase. (See CONTEXT.md → Group.)

### Rules-in-play block (runs on both paths, after Exploration)

This block does **not** decide architecture — the project's rule-ADRs already do. It only identifies which of them this change operates under, so the implementer knows the boundaries and the reviewer knows where to look. The implementer keeps freedom on *how* the code is written within those rules.

- From the rule-ADRs read during Exploration, pick the ones this change operates under — match the layers, modules, and patterns it touches against each rule's `**Scope:**` line, or against the rule text itself when unscoped. **Account for every rule-ADR**: each is either listed or consciously excluded as untouched. Skip any marked `Status: deprecated`; a superseded rule resolves to the ADR that replaced it. This becomes `## Rules in play`. If none apply, say so; the general rule set still governs at review.
- If the change puts pressure on a structural choice **no rule covers**, decide with the user whether it is *project-wide* (would recur beyond this plan) or *plan-local throwaway*. Project-wide → don't bake a decision into the plan; recommend running `codebase-rules` to add a rule-ADR first, then reference it. Plan-local → leave it to the implementer; the reviewer catches problems against the rules.

Draft from Exploration first — don't grill choices the rule-ADRs already settle.

### Final grill steps — universal

These steps run **regardless of which Detection-order branch you took** — they apply to **both the standalone path and the from-issue path**. Do not skip them on the from-issue path.

1. **Draft the whole plan content in one continuous pass, without a separate stop-and-confirm after each piece.** Cover, in this order, using your own recommendation to keep momentum (still a `grilling` session underneath — recommendation first, explore before asking — but aimed at one shared understanding, not a checkpoint per section):
   - `## Acceptance criteria`: numbered `AC-N` list, terse — outcome + verify clause, sacrifice grammar for brevity. The verify clause should name the concrete automated test that will prove it (e.g. `AC-1: login redirects to dashboard. Verify: tests/test_login.py::test_admin_redirect.`) — that exact test gets written in `Phase 1 — Red` and re-run in Verification. Tag `(manual)` only when no automated test is possible; those get a plain-English check instead of a test path. From-issue plans render the issue's lifted criteria; standalone plans render what the WHAT-grill produced.
   - `## Rules in play`: the `ADR-NNNN` rule-ADRs from the Rules-in-play block — link + that ADR's `**Rule:**` line **verbatim**, never paraphrased (the ADR is the single source of truth), so the implementer and reviewer load only what applies. No plan-local structural decisions; if none apply, a single line saying the general rule set governs.
   - **Plan structure**, test-driven and fixed at three anchor positions:
     - `## Phase 0 — Preflight` (no Groups): only genuine blockers that must clear before execution can start — an external credential, a created resource, a decision that can't be made until execution time. Not an assumption-confirmation checklist. If there are none, render a single row reading `None` so execution goes straight to Red.
     - `## Phase 1 — Red` (mandatory, always second): one or more Groups that write the actual failing (red) automated tests named in each non-`(manual)` `AC-N`'s verify clause, using the project's existing test framework/conventions (from Exploration). No implementation code is written here — the tests should fail because the behavior doesn't exist yet, not because of a broken test. Skip this phase's content (leave it a stub noting "no automatable criteria") only if every `AC-N` is `(manual)`.
     - `Phase 2 — Green: <name>` through the second-to-last phase: the Green phases — implementation Groups that make the Red tests pass. Name each `Phase K — Green: <short phase name>`.
     - `## Phase N — Verification` (mandatory, always last, see template): a single acceptance-criteria check that re-runs each Phase-1 test and confirms it now passes green, plus confirms any `(manual)` criteria with the user. It sweeps **no** architecture — a separate code-review session judges that against the committed diff. Writes **no new code**.
     - **Every Group within any phase (including Phase 1) must be a fully independent vertical slice** — verifiable on its own, with no read-dependency on any sibling Group in the same phase, and no shared-file writes with any sibling Group. A cross-Group read-dependency or shared-file write is a plan defect: it means the Groups aren't really separate work, and `implementation-plan-execute` can't implement and verify one Group without pulling in another's half-finished change. Self-check each phase: *"Could I implement and verify this Group on its own, without anything from a sibling Group in the same phase?"* If not, merge those Groups, split the file first, or move one Group to a later phase.
   - **Branch**: which git branch the implementer should work from.
     - **From-issue path:** the issue already named it. Take the slug from the issue body's `## Branch` section and prepend the GitHub issue number: slug `oauth-admin-login` on issue #42 → `42-oauth-admin-login`. This is not a grill topic — state the assembled name in the draft and move on. Only if the issue has no `## Branch` section (older issue) fall back to `<issue-number>-<plan slug>`.
     - **Standalone path:** a new branch named after the plan slot/slug, or an existing one the user names.
   If drafting any of these surfaces a gap in an earlier piece (a missing rule reference, a missing AC), fix it inline rather than treating the pieces as locked in sequence — this is one draft, not four.
2. **Present the complete combined draft once** — Acceptance criteria, Rules in play, plan structure with Groups, and Branch — together, with 1-2 sentences of reasoning per Group. **Wait for the user to confirm or correct the whole thing.** Iterate on the combined draft together until the user agrees it's the full contract for "done" — don't re-split this back into separate per-section stops.

Only **after the combined draft is confirmed**, say:

> "I think we've covered everything. Creating the implementation plan now."

Then proceed immediately to Phase 2 — do not wait for the user to prompt you.

---

## Phase 2 — Write the plan

1. **Read the template** at `~/.claude/skills/implementation-planning/template_implementation_plan.md` before writing anything.

2. **Determine plan number** based on the Detection-order branch:
   - **From-issue path (cases 1 and 2):** use the slot derived on the from-issue path — the ID tag verbatim if the issue is tagged, otherwise the GitHub issue number. Do **not** pick the next free slot in `implementation_plans/` — the issue is authoritative. If a plan file with that slot already exists, stop and ask the user how to resolve (overwrite, rename existing, etc.) rather than silently picking a different slot.
   - **Standalone path (case 3):** list files in `implementation_plans/` at the project root to find the next available `N.N` slot. If the directory doesn't exist, create it and start at `1.1`.

3. **Create and switch to the branch** — before writing the plan file, so the plan itself lands on the branch it describes. Use the confirmed `**Branch:**` name: `git checkout -b <branch>`, or `git checkout <branch>` if it already exists. If the working tree carries unrelated uncommitted changes, surface that to the user before switching rather than dragging them across. Do not commit the plan file — leave it staged-or-untracked for `implementation-plan-execute` to commit with the work.

4. **Write the plan file** to `implementation_plans/<slot>_short_name.md`. Derive `short_name` based on the Detection-order branch:
   - **From-issue path (cases 1 and 2):** `short_name` is **1–3 words, snake_case, no articles** — just enough to skim a directory listing. The slot already identifies which issue the plan tackles, so the slug does not need to mirror the full issue title. Pick the most load-bearing nouns/verbs from the issue title; drop the ID tag (if any), the `[feature]` / `[bug]` prefix, and any filler. Example: tagged issue `(1.3) [feature] Add OAuth login for admin dashboard` → `1.3_oauth_login.md`. Example: untagged issue `#42 [feature] skill: generate test structure from codebase + docs` → `42_test_structure.md`.
   - **Standalone path (case 3):** `short_name` is 2–4 words, snake_case, no articles.

5. **Follow the template exactly** for section shape, order, and content — it was already read in step 1. Populate `## Acceptance criteria` and `## Rules in play` from the confirmed combined draft; populate `**Branch:**` from the confirmed branch decision; don't invent content beyond what Phase 1 confirmed. Keep `AC-N` and rule references terse — sacrifice grammar for brevity, one line each, no restating the same point twice. The one thing the template can't tell you — the title line derivation:
   - Title line: `# <slot> — Plan Name`. From-issue path: `Plan Name` **mirrors the issue title verbatim, with the ID tag stripped if there was one** (keep the `[feature]` / `[bug]` prefix and original casing/punctuation), followed by ` (#<issue-number>)`. Example (tagged): `# 1.3 — [feature] Add OAuth login for admin dashboard (#42)`. Example (untagged): `# 42 — [feature] Add OAuth login for admin dashboard (#42)`. Standalone path: a short human-readable title derived from the grill.

6. **Rules**:
   - Name a specific file in every task row where possible; use `—` only when genuinely unknown
   - Don't invent decisions not established in the grill session
   - The Claude Instructions section must capture all constraints and "do not" rules surfaced during grilling
   - The Claude Instructions section must include a `**Rules binding:**` rule: *"Stay within the rule-ADRs in `docs/adr/` (those named in `## Rules in play` apply directly). You have freedom on how to implement within them; you do not need per-Group architecture approval. If the change forces a structural choice no rule covers and it's project-wide, stop and flag it for a `codebase-rules` ADR rather than improvising a one-off. The code-review session enforces the rule-ADRs on the commit."*
   - No Group or Phase (other than the final `Phase N — Verification`) carries a test/check block — testing is not interleaved. Note this in Claude Instructions under **Testing**: nothing is verified until the final Verification phase, and that phase re-runs the tests written in `Phase 1 — Red` rather than inventing new checks.

7. **Phase shape**: `Phase 1` onward renders as `### Group N — short name` sub-sections (description, then the task table — no architecture block) — see the template for the exact rendering. No functionality/architecture test blocks per Group or per phase-integration. Phase 0 (Preflight) stays a single task table with no groups; each row is a genuine blocker to be cleared before execution starts, or a lone `None` row when there are none. `Phase 1 — Red` is always second and always present, even if trivial. `Phase N — Verification` is a single acceptance-criteria check (no architecture sweep) exactly as in the template — that's the one place tests actually run.

8. Output a clickable markdown link to the new plan file as the last line of your response.
</content>
