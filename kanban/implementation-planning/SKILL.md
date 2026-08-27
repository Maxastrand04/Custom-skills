---
name: implementation-planning
description: Grill the user into a binding public interface covering names, parameters, return values, and contracts, then write a test-driven implementation plan to implementation_plans/N.N_short_name.md. Use when user wants to plan a feature or task, says "let's plan", "implementation plan", or "grill me then plan".
---

# implementation-planning

Two phases: grill the user to reach shared understanding, then write the whole plan in one pass.

**The user owns the contract; the implementer owns everything behind it. This binds all generated plans.** A plan's `## Public interface` fixes the names, parameters, return values, and documented behaviour of every entry point the change adds or alters. That is the one structural thing a plan decides, and what the grill drives hardest toward. Everything inside the boundary, meaning helpers, control flow, and data structures, is the implementer's call, and gets cleaned up by the separate code-review session.

Every plan runs the TDD loop at the phase level. `## Phase 0: Prerequisites` confirms the ground the plan stands on exists and is green. `## Phase 1: Red` writes the acceptance tests and runs them, and every one must fail. The Green phases fill the stubs those tests call. `## Phase N: Verification` runs them again, and any failure sends the plan back to Green. Green and Verification loop until the whole suite is green, and only then does the work commit.

---

## Phase 1: Grill session

You are a developer grilling a project leader about code and product structure. Every question asked anywhere in this phase runs under the `grilling` skill's interview mechanics, so invoke it. This skill supplies *what* to ask and in what order; `grilling` supplies *how*.

The phase runs as **one continuous session toward a single reached understanding**, not a series of checkpoints. Draft as you go, present work back only when something is genuinely open, and take exactly one confirmation gate at the end. See Final grill steps.

### Detection order

Before any grill content runs, route the session by checking these three cases in order. Stop at the first match:

1. **Explicit `<issue-ref>` arg.** The user invoked the skill with the **GitHub issue number** (`42` or `#42`), a full GitHub issue URL, or a natural-language description of an existing issue. The GitHub number is the canonical way in, so resolve URLs and descriptions down to it via `gh issue list` and `gh issue view`. Jump directly to the **from-issue path**.
2. **Auto-detect, strict and confirmed.** Applies only when **both** gates hold: `new-ticket` ran in the **current session** and posted an issue, leaving a fresh issue URL in conversation context, AND the user explicitly confirms when prompted. Even when the first gate holds, **always prompt before skipping the WHAT-grill**. Never auto-route silently.
3. **Standalone fallback.** Neither matched. Run the full grill below.

### From-issue path

Triggered by case 1 or a confirmed case 2:

- **Skip the WHAT topics, run the HOW topics only.** Scope, behavior, and out-of-scope are already settled by the issue body, so take them as given. The public interface, files, and rollout are not in the issue and must be resolved before writing the plan.
- **Read the issue body first**, in full, with `gh issue view <ref> --json title,body,labels`, so the HOW questions are grounded in the issue's WHAT.
- **Lift acceptance criteria from the issue.** Parse the body for explicit acceptance criteria, "Done when" text, or checklist items, and assign each an `AC-N` ID. These feed the combined draft at the end. Don't stop for a separate confirmation here.
- **Capture the issue title and number, and derive the plan slot** for Phase 2, so the plan filename and title mirror the issue and the link is obvious at a glance. Two title conventions are both valid:
  - **Tagged.** The title leads with an `(N)` or `(N.M)` token, which is what `epic-planning` tickets carry. The slot is that token verbatim: `(1.3) [feature] …` gives slot `1.3`.
  - **Untagged.** No leading token, which is what `new-ticket` tickets carry. The slot is the GitHub issue number: `#42` gives slot `42`.

  Never ask the user to retitle an issue to fit a convention.

- **Capture the branch slug** from the issue body's `## Branch` section. The implementing branch is `<issue-number>-<slug>`. The issue chose the slug, this skill supplies the number.

### Exploration step, runs first on both paths

Before asking any questions, ground the grill in what already exists:

1. **Fixed project-level reads**, always, where present: `CONTEXT.md`, top-level `README.md`, a directory listing of the project root, `implementation_plans/` for prior plans, and `docs/adr/` for recorded decisions and rules. These ground the grill by informing what the interface should look like and what language to name it in. The plan does not restate them. The code-review session enforces the rules against the committed diff.
2. **Targeted change-specific reads.** Grep and read the modules likely to be touched, neighboring code, and the **existing public surface** the new interface must sit beside, covering signatures, naming, error types, and module layout.

Then emit a short **"What I found"** summary covering the relevant modules, the conventions visible in the affected area, the public surface the change plugs into, and prior plans touching the same code. **Wait for the user to correct misreads.** Corrections are cheap here and propagate downstream.

### Grill order

WHAT topics, meaning scope, behavior, and out-of-scope, then acceptance criteria, then the **Public-interface block**, then the **Prerequisites sweep**, then remaining HOW, meaning data model, error handling, rollout order, and known constraints. Drive the acceptance criteria out of the WHAT-grill by asking, for each scope or behavior item, *"How would we know this is done?"* On the from-issue path the WHAT topics are skipped, collapsing this to Exploration, then the Public-interface block, then the Prerequisites sweep, then remaining HOW.

### Public-interface block, runs on both paths

**The hardest-grilled part of the session.** The interface is the contract the implementer is held to, so it gets settled here, with the user, before any plan exists.

For every entry point the change adds or alters, drive four things to a settled answer:

1. **Name.** The exact identifier, in the naming style Exploration found.
2. **Parameters.** Each one's name, type, whether it's required, and its default.
3. **Return value.** Its type, and what it *means* to the caller.
4. **Contract.** What the caller may rely on: errors raised and when, edge-case behaviour, invariants, side effects.

Rules for this block:

- **Nothing is settled while any of the four is open.** A parameter with no type, a return described only as "the result", an error path nobody named. Each is an unresolved branch. Keep going.
- **Grill the interface, not the implementation.** "One function or a class with three methods?" is the contract, so grill it. "A dict or an LRU cache for the tokens?" sits behind the boundary, so don't spend the user's attention on it, and don't let a plan-local implementation choice into the plan.
- **Cover every `AC-N`.** Each non-`(manual)` criterion must be exercisable through something on the list. A criterion no signature can reach means the contract is incomplete, so surface the gap and resolve it.
- **Render as stubs.** The output is fenced code, grouped by file, carrying the signature, the contract as the docstring, and a `NotImplementedError` body. That stub text is what the plan carries and what the implementer copies, so write it in the project's actual language and style, not pseudocode.

Draft from Exploration first. Propose the interface that fits the existing surface and let the user correct it, rather than asking from a blank page.

### Prerequisites sweep

The interface is settled, so now work out what it stands on. **Anything the implementation relies on but does not build is a prerequisite**, and the plan lists it so the implementer can confirm it before writing a line.

**Name the pillar, not the check.** The sweep is a WHAT, matching the rest of the chain: each row says what has to exist and work, and the implementer works out how to confirm it during Phase 0. Don't write a command, a test path, or an assertion into a row. Deciding how to check is the implementer's call, the same way everything behind `## Public interface` is.

Draft the list from Exploration rather than asking cold. You already read the modules the change touches, so propose it and let the user correct it. Sweep for:

- **Modules and functions** the implementation calls but doesn't write.
- **Data it reads**: models, fields, tables, config keys.
- **Features that must already work** end to end, wherever this change extends something rather than replacing it.
- **Files the plan modifies**, which have to exist to be modified.
- **Shared test fixtures, factories, or helpers** the `Phase 1: Red` tests will lean on, plus the directory those test files land in.
- **Third-party libraries** the `## Public interface` stubs import.
- **External resources**: a credential, a running service, a created bucket or queue.

**Every row has to be unambiguous.** Ask whether two readers would go and confirm the same thing. "Auth works" fails that, since one reader checks that a login returns a session and another checks that expired tokens are rejected. Sharpen it with the user until the row names one capability, or drop it. Pick the verb carefully, since it is what sets the bar in Phase 0: a row that says something *exists* is settled by finding it, and a row that says something *works* is not.

**Then ask the question the sweep exists for: is any of this missing or broken today?** Check the ones you can while drafting. Anything absent is work that has to land before this plan can run, so surface it and let the user decide whether it joins this plan, becomes its own, or blocks it. A plan that quietly assumes a module someone still has to write is the failure this sweep prevents.

### Final grill steps, universal

These run on **both paths**. Do not skip them on the from-issue path.

1. **Draft the whole plan content in one continuous pass**, in this order, leading with your own recommendation to keep momentum:
   - `## Acceptance criteria`: a numbered `AC-N` list, terse, each an outcome plus a verify clause. The verify clause names the concrete automated test that will prove it, as in `AC-1: login redirects to dashboard. Verify: tests/test_login.py::test_admin_redirect.` That exact test gets written and run red in `Phase 1: Red`, then run again in Verification. Tag `(manual)` only when no automated test is possible; those get a plain-English check instead of a test path. From-issue plans render the issue's lifted criteria; standalone plans render what the WHAT-grill produced.
   - `## Public interface`: the stubs settled above, grouped by file, verbatim.
   - **Plan structure**, fixed at three anchor positions, each phase a single flat task table.
     - `## Phase 0: Prerequisites` renders the Prerequisites sweep, one row per pillar the implementation relies on but doesn't build, each with a `Where`. It carries no check column; the implementer decides how to confirm each row. It is not a list of what the plan builds and not an assumption-confirmation checklist. If the implementation stands on nothing pre-existing, write a single row reading `None`.
     - `## Phase 1: Red` is mandatory and always second. It carries one row per non-`(manual)` `AC-N`, naming the **test function** from that criterion's verify clause and the **file** it goes in, and nothing else. The rows deliberately don't say what each test asserts; the implementer derives that from the criterion. The phase ends by running them and confirming every one fails. Leave the phase a stub noting "no automatable criteria" only if every `AC-N` is `(manual)`.
     - `Phase 2: Green: <name>` through the second-to-last phase hold the implementation tasks that make the Red tests pass. Every stub in `## Public interface` gets a row telling the implementer to copy it in and fill the body.
     - `## Phase N: Verification` is mandatory and always last. It carries one row per `AC-N`, running each Phase-1 test and confirming green, plus confirming `(manual)` criteria with the user. It writes **no new code** and judges no implementation quality. Any failure sends the plan back to a Green phase, and Green and Verification repeat until every row is green.
   - **Branch**:
     - **From-issue path.** The issue already named it, so take the slug from its `## Branch` section and prepend the issue number: slug `oauth-admin-login` on #42 gives `42-oauth-admin-login`. This is not a grill topic. State the assembled name and move on. If the issue has no `## Branch` section, which happens on older issues, fall back to `<issue-number>-<plan slug>`.
     - **Standalone path.** A new branch named after the plan slot and slug, or an existing one the user names.

   If drafting one piece surfaces a gap in an earlier one, such as a missing signature or a missing AC, fix it inline. This is one draft, not four.
2. **Present the complete combined draft once**, with acceptance criteria, public interface, prerequisites, plan structure, and branch together, and 1-2 sentences of reasoning per phase. **Wait for the user to confirm or correct the whole thing**, and iterate on it as a whole until they agree it's the full contract for "done".

Only **after the combined draft is confirmed**, say:

> "I think we've covered everything. Creating the implementation plan now."

Then proceed immediately to Phase 2. Do not wait for the user to prompt you.

---

## Phase 2: Write the plan

1. **Read the template** at `~/.claude/skills/implementation-planning/template_implementation_plan.md` before writing anything.

2. **Determine the plan slot:**
   - **From-issue path.** Use the slot derived above, meaning the ID tag verbatim if tagged, otherwise the GitHub issue number. Do **not** pick the next free slot in `implementation_plans/`; the issue is authoritative. If a plan with that slot exists, stop and ask the user how to resolve it rather than silently picking another.
   - **Standalone path.** List `implementation_plans/` and take the next free `N.N`. If the directory doesn't exist, create it and start at `1.1`.

3. **Create and switch to the branch** before writing the plan file, so the plan lands on the branch it describes. Run `git checkout -b <branch>`, or `git checkout <branch>` if it exists. If the working tree carries unrelated uncommitted changes, surface that before switching rather than dragging them across. Do not commit the plan file; leave it for `implementation-plan-execute` to commit with the work.

4. **Write the plan file** to `implementation_plans/<slot>_short_name.md`:
   - **From-issue path.** `short_name` is 1-3 words, snake_case, no articles, just enough to skim a directory listing. The slot already identifies the issue, so the slug needn't mirror the full title. Take the most load-bearing nouns and verbs, and drop the ID tag, the `[feature]` or `[bug]` prefix, and any filler. Examples: `(1.3) [feature] Add OAuth login for admin dashboard` gives `1.3_oauth_login.md`; `#42 [feature] skill: generate test structure from codebase + docs` gives `42_test_structure.md`.
   - **Standalone path.** `short_name` is 2-4 words, snake_case, no articles.

5. **Follow the template exactly** for section shape, order, and content. Populate `## Acceptance criteria` and `## Public interface` from the confirmed draft, and `**Branch:**` from the confirmed branch decision, and invent nothing beyond what Phase 1 confirmed. The one thing the template can't tell you is the title line `# <slot>: Plan Name`:
   - **From-issue path.** `Plan Name` **mirrors the issue title verbatim with the ID tag stripped**, keeping the `[feature]` or `[bug]` prefix and the original casing and punctuation, followed by ` (#<issue-number>)`. Examples: `# 1.3: [feature] Add OAuth login for admin dashboard (#42)`; `# 42: [feature] Add OAuth login for admin dashboard (#42)`.
   - **Standalone path.** A short human-readable title from the grill.

6. **Rules**:
   - Keep every line terse. Sacrifice grammar for brevity, and never restate the same point twice.
   - `## Public interface` carries the confirmed stubs **verbatim**, meaning signature, docstring contract, and `NotImplementedError` body. Never paraphrase a signature into prose; the stub is what gets copied.
   - Name a specific file in every task row where possible, and write `TBD` only when it is genuinely unknown.
   - Don't invent decisions not established in the grill session.
   - Claude Instructions must capture all constraints and "do not" rules surfaced during grilling.

7. Output a clickable markdown link to the new plan file as the last line of your response.
