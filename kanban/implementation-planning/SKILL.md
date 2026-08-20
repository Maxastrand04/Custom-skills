---
name: implementation-planning
description: Grill the user into a binding public interface — names, parameters, return values, contracts — then write a test-driven implementation plan to implementation_plans/N.N_short_name.md. Use when user wants to plan a feature or task, says "let's plan", "implementation plan", or "grill me then plan".
---

# implementation-planning

Two phases: grill the user to reach shared understanding, then write the whole plan in one pass.

**The user owns the contract; the implementer owns everything behind it (binds all generated plans):** a plan's `## Public interface` fixes the names, parameters, return values, and documented behaviour of every entry point the change adds or alters. That is the one structural thing a plan decides, and what the grill drives hardest toward. Everything inside the boundary — helpers, control flow, data structures — is the implementer's call, and is cleaned up by the separate code-review session.

Every plan is test-driven at the phase level and carries no test block before the end: `## Phase 1 — Red` names the tests to write, the Green phases fill the stubs until they pass, and the mandatory final `Phase N — Verification` is the single source of truth for "does it work" (see `implementation-plan-execute`'s Verification failure rule).

---

## Phase 1 — Grill session

You are a developer grilling a project leader about code and product structure. Every question asked anywhere in this phase runs under the `grilling` skill's interview mechanics: invoke it. This skill supplies *what* to ask and in what order; `grilling` supplies *how*.

The phase runs as **one continuous session toward a single reached understanding**, not a series of checkpoints — draft as you go, present work back only when something is genuinely open, and take exactly one confirmation gate at the end (see Final grill steps).

### Detection order

Before any grill content runs, route the session by checking these three cases in order. Stop at the first match:

1. **Explicit `<issue-ref>` arg** — the user invoked the skill with the **GitHub issue number** (`42` or `#42`), a full GitHub issue URL, or a natural-language description of an existing issue. The GitHub number is the canonical way in; resolve URLs and descriptions down to it via `gh issue list` / `gh issue view`. Jump directly to the **from-issue path**.
2. **Auto-detect (strict + confirm)** — only when **both** gates hold: (a) `new-issue` ran in the **current session** and posted an issue (you have a fresh issue URL in conversation context), AND (b) the user explicitly confirms when prompted. Even when (a) holds, **always prompt before skipping the WHAT-grill** — never auto-route silently.
3. **Standalone fallback** — neither matched. Run the full grill below.

### From-issue path

Triggered by case (1) or a confirmed case (2):

- **Skip the WHAT topics, run the HOW topics only.** Scope, behavior, and out-of-scope are already settled by the issue body — take them as given. The public interface, files, and rollout are not in the issue and must be resolved before writing the plan.
- **Read the issue body first** — `gh issue view <ref> --json title,body,labels` — in full, so the HOW questions are grounded in the issue's WHAT.
- **Lift acceptance criteria from the issue.** Parse the body for explicit acceptance criteria / "Done when" / checklist items; assign each an `AC-N` ID. These feed the combined draft at the end — don't stop for a separate confirmation here.
- **Capture the issue title and number, and derive the plan slot** for Phase 2 — the plan filename and title mirror the issue so the link is obvious at a glance. Two title conventions are both valid:
  - **Tagged** — the title leads with an `(N)` or `(N.M)` token (`epic-planning` tickets). Slot = that token verbatim: `(1.3) [feature] …` → slot `1.3`.
  - **Untagged** — no leading token (`new-issue` issues). Slot = the GitHub issue number: `#42` → slot `42`.

  Never ask the user to retitle an issue to fit a convention.

- **Capture the branch slug** from the issue body's `## Branch` section. The implementing branch is `<issue-number>-<slug>` — the issue chose the slug, this skill supplies the number.

### Exploration step (runs first, both paths)

Before asking any questions, ground the grill in what already exists:

1. **Fixed project-level reads** (always, if present): `CONTEXT.md`, top-level `README.md`, a directory listing of the project root, `implementation_plans/` for prior plans, and `docs/adr/` for recorded decisions and rules. These ground the grill — they inform what the interface should look like and what language to name it in. The plan does not restate them; the code-review session enforces the rules against the committed diff.
2. **Targeted change-specific reads**: grep/read the modules likely to be touched, neighboring code, and the **existing public surface** the new interface must sit beside — signatures, naming, error types, module layout.

Then emit a short **"What I found"** summary: the relevant modules, the conventions visible in the affected area, the public surface the change plugs into, and prior plans touching the same code. **Wait for the user to correct misreads** — corrections are cheap here and propagate downstream.

### Grill order

WHAT topics (scope, behavior, out-of-scope) → acceptance criteria (drive out of the WHAT-grill: for each scope/behavior item, ask *"How would we know this is done?"*) → **Public-interface block** → remaining HOW (data model, error handling, rollout order, known constraints). On the from-issue path the WHAT topics are skipped, collapsing this to Exploration → Public-interface block → remaining HOW.

### Public-interface block (runs on both paths)

**The hardest-grilled part of the session.** The interface is the contract the implementer is held to, so it gets settled here, with the user, before any plan exists.

For every entry point the change adds or alters, drive four things to a settled answer:

1. **Name** — the exact identifier, in the naming style Exploration found.
2. **Parameters** — each one's name, type, whether it's required, and its default.
3. **Return value** — its type, and what it *means* to the caller.
4. **Contract** — what the caller may rely on: errors raised and when, edge-case behaviour, invariants, side effects.

Rules for this block:

- **Nothing is settled while any of the four is open.** A parameter with no type, a return described only as "the result", an error path nobody named — each is an unresolved branch. Keep going.
- **Grill the interface, not the implementation.** "One function or a class with three methods?" is the contract — grill it. "A dict or an LRU cache for the tokens?" is behind the boundary — don't spend the user's attention on it, and don't let a plan-local implementation choice into the plan.
- **Cover every `AC-N`.** Each non-`(manual)` criterion must be exercisable through something on the list. A criterion no signature can reach means the contract is incomplete — surface the gap and resolve it.
- **Render as stubs.** The output is fenced code, grouped by file: signature, contract as the docstring, `NotImplementedError` body. That stub text is what the plan carries and what the implementer copies — so write it in the project's actual language and style, not pseudocode.

Draft from Exploration first — propose the interface that fits the existing surface and let the user correct it, rather than asking from a blank page.

### Final grill steps — universal

These run on **both paths**. Do not skip them on the from-issue path.

1. **Draft the whole plan content in one continuous pass**, in this order, leading with your own recommendation to keep momentum:
   - `## Acceptance criteria`: numbered `AC-N` list, terse — outcome + verify clause. The verify clause names the concrete automated test that will prove it (e.g. `AC-1: login redirects to dashboard. Verify: tests/test_login.py::test_admin_redirect.`) — that exact test gets written in `Phase 1 — Red` and re-run in Verification. Tag `(manual)` only when no automated test is possible; those get a plain-English check instead of a test path. From-issue plans render the issue's lifted criteria; standalone plans render what the WHAT-grill produced.
   - `## Public interface`: the stubs settled above, grouped by file, verbatim.
   - **Plan structure** — fixed at three anchor positions, each phase a flat task table (plans carry no Groups):
     - `## Phase 0 — Preflight`: only genuine blockers that must clear before execution starts — an external credential, a created resource, a decision that can't be made until execution time. Not an assumption-confirmation checklist. If there are none, a single row reading `None`.
     - `## Phase 1 — Red` (mandatory, always second): one row per non-`(manual)` `AC-N`, naming the **test function** from that criterion's verify clause and the **file** it goes in — nothing else. The rows deliberately don't say what each test asserts; the implementer derives that from the criterion. Leave the phase a stub noting "no automatable criteria" only if every `AC-N` is `(manual)`.
     - `Phase 2 — Green: <name>` through the second-to-last phase: implementation tasks that make the Red tests pass. Every stub in `## Public interface` gets a row telling the implementer to copy it in and fill the body.
     - `## Phase N — Verification` (mandatory, always last): one row per `AC-N`, re-running each Phase-1 test and confirming green, plus confirming `(manual)` criteria with the user. Writes **no new code** and judges no implementation quality.
   - **Branch**:
     - **From-issue path:** the issue already named it — take the slug from its `## Branch` section and prepend the issue number (slug `oauth-admin-login` on #42 → `42-oauth-admin-login`). Not a grill topic; state the assembled name and move on. If the issue has no `## Branch` section (older issue), fall back to `<issue-number>-<plan slug>`.
     - **Standalone path:** a new branch named after the plan slot/slug, or an existing one the user names.

   If drafting one piece surfaces a gap in an earlier one (a missing signature, a missing AC), fix it inline — this is one draft, not four.
2. **Present the complete combined draft once** — Acceptance criteria, Public interface, plan structure, and Branch together, with 1-2 sentences of reasoning per phase. **Wait for the user to confirm or correct the whole thing**, and iterate on it as a whole until they agree it's the full contract for "done".

Only **after the combined draft is confirmed**, say:

> "I think we've covered everything. Creating the implementation plan now."

Then proceed immediately to Phase 2 — do not wait for the user to prompt you.

---

## Phase 2 — Write the plan

1. **Read the template** at `~/.claude/skills/implementation-planning/template_implementation_plan.md` before writing anything.

2. **Determine the plan slot:**
   - **From-issue path:** the slot derived above — the ID tag verbatim if tagged, otherwise the GitHub issue number. Do **not** pick the next free slot in `implementation_plans/`; the issue is authoritative. If a plan with that slot exists, stop and ask the user how to resolve it rather than silently picking another.
   - **Standalone path:** list `implementation_plans/` and take the next free `N.N`. If the directory doesn't exist, create it and start at `1.1`.

3. **Create and switch to the branch** — before writing the plan file, so the plan lands on the branch it describes: `git checkout -b <branch>`, or `git checkout <branch>` if it exists. If the working tree carries unrelated uncommitted changes, surface that before switching rather than dragging them across. Do not commit the plan file — leave it for `implementation-plan-execute` to commit with the work.

4. **Write the plan file** to `implementation_plans/<slot>_short_name.md`:
   - **From-issue path:** `short_name` is **1–3 words, snake_case, no articles** — just enough to skim a directory listing. The slot already identifies the issue, so the slug needn't mirror the full title. Take the most load-bearing nouns/verbs and drop the ID tag, the `[feature]` / `[bug]` prefix, and any filler. Examples: `(1.3) [feature] Add OAuth login for admin dashboard` → `1.3_oauth_login.md`; `#42 [feature] skill: generate test structure from codebase + docs` → `42_test_structure.md`.
   - **Standalone path:** `short_name` is 2–4 words, snake_case, no articles.

5. **Follow the template exactly** for section shape, order, and content. Populate `## Acceptance criteria` and `## Public interface` from the confirmed draft, `**Branch:**` from the confirmed branch decision, and invent nothing beyond what Phase 1 confirmed. The one thing the template can't tell you — the title line `# <slot> — Plan Name`:
   - **From-issue path:** `Plan Name` **mirrors the issue title verbatim with the ID tag stripped** (keep the `[feature]` / `[bug]` prefix and original casing/punctuation), followed by ` (#<issue-number>)`. Examples: `# 1.3 — [feature] Add OAuth login for admin dashboard (#42)`; `# 42 — [feature] Add OAuth login for admin dashboard (#42)`.
   - **Standalone path:** a short human-readable title from the grill.

6. **Rules**:
   - Keep every line terse — sacrifice grammar for brevity, no restating the same point twice.
   - `## Public interface` carries the confirmed stubs **verbatim** — signature, docstring contract, `NotImplementedError` body. Never paraphrase a signature into prose; the stub is what gets copied.
   - Name a specific file in every task row where possible; use `—` only when genuinely unknown.
   - Don't invent decisions not established in the grill session.
   - Claude Instructions must capture all constraints and "do not" rules surfaced during grilling.

7. **Phase shape**: every phase is a single flat task table — no Groups, no per-phase test blocks. `Phase 1 — Red` is always second and always present, and its table is `Test function | File | Status` with no task descriptions. Green phases use `Task | File | Status`. `Phase N — Verification` is one row per `AC-N` — the one place tests actually run.

8. Output a clickable markdown link to the new plan file as the last line of your response.
