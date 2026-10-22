---
name: new-ticket
description: Beside the board, for standalone work no epic covers. Grills a ticket down to WHAT, never HOW, sets its effort level, publishes it as a GitHub issue, and splits it into sub-issues if it is too big. For epic-linked work, use map-epic.
disable-model-invocation: true
---

# new-ticket

Grill the user into a single, well-scoped GitHub ticket covering **WHAT** changes, meaning the pieces of the solution, how control flows between them, and scope, and never **HOW**, meaning names, files, signatures, and tests. Publish via `gh`. Optionally split into vertical-slice sub-issues. Give every task ticket an effort level, which decides how much of the user the ticket needs and which route solves it.

The published body is deliberately thin. The grill is not. Everything the grill surfaces must land as a **Spec** line, an Out-of-scope line, or be consciously dropped.

Read the bundled files at runtime. Do not assume their contents from this document:

- **`ticket-shapes.md` is the single source of truth** for body shape, title format, labels, effort criteria, branch slug, the AI disclaimer, gh preflight, the publish loop, and native wiring.
- `subissue-splitting.md` holds the vertical-slice rule and the two-tier coverage check.

Read `ticket-shapes.md` and run its **gh preflight** before any grilling.

---

## Invocation

Two modes:

1. **Cold start.** The user invokes with no extra text. Open with the first grill turn, feat vs fix.
2. **One-liner seed.** The user invokes with a short phrase such as "users can sign up with email". Treat that phrase as **the seed of the grill, not a finished ticket body.** Every grill topic still runs.

If the user's phrase looks epic-linked, meaning it references an epic task, a `(N.M)` id, or an `epic: (N)` issue, point them at `/map-epic` instead. This skill does not resolve epic refs.

Do **not** synthesise a ticket from prior conversation context.

---

## First grill turn, feat vs fix

The first question is always: **"Is this a feat or a fix?"** Ask once. Do not infer.

The answer picks the **grill agenda** below and the type on the published title, `feat:` or `fix:`. It does **not** change the body shape or the labels.

---

## The grill, WHAT only

You are a developer grilling a product owner about product requirements. Invoke the `grilling` skill for the interview mechanics, and work the agenda one topic at a time.

**Feat agenda:**

1. Problem and motivation: the user-visible problem, and why now.
2. Target user or actor: who triggers or benefits.
3. Trigger or entry point: how the user reaches the behaviour.
4. Pieces: what parts the solution adds or alters, and what each one carries.
5. Flow: the happy path step by step, from the trigger to the result, naming which piece acts at each step.
6. Edge cases and failure modes: missing, invalid, or conflicting inputs, and operations that can't complete.
7. Dependencies on existing functionality: behaviours this relies on or disturbs.
8. Out of scope: what might look related but isn't.

**Fix agenda:**

1. Symptom: what the user sees go wrong.
2. Reproduction steps: the minimal sequence that triggers it.
3. Expected vs actual, at the point of failure.
4. Scope of impact: who hits it, how often, and whether it blocks or annoys.
5. Conditions: user state, surface, and inputs under which it reproduces.
6. First seen or regression: always broken, or a regression from a known-good state.
7. Workarounds known: what users can do today, or "none known".
8. Corrected flow: which piece goes wrong, and the steps as they should run.
9. Out of scope: related bugs or refactors this fix won't touch.

**Drive every topic to an outcome.** For each answer, ask *"which piece does what, and what happens next?"* and write that as one terse line. A topic that leaves no Interface, Behaviour, or Out-of-scope line has left nothing in the ticket, so say so and resolve it before moving on. Every `fix` ticket carries one standing Behaviour line: the reproduction steps no longer produce the symptom.

**The Spec is the user's picture of the solution.** They read it and check it mirrors how they expect the goal to be reached. Write it like pseudocode: concrete enough to trace through the code, short enough to read at a glance.

**Describe pieces, never name them.** "A session check runs before each page load" and "Expired sessions send the user back to login" belong here. "`refresh_token` raises `AuthError` on an expired token" does not, however true it turns out to be. If you catch yourself reaching for a symbol name to say it precisely, the precision belongs to `architect-ticket`.

**Never settled in this ticket.** These are HOW topics, and they defer to `architect-ticket`:

- File paths, module names, function or class names, function signatures
- Schema design, database tables, API contract shapes
- Test names, test file locations, what any test asserts
- Rollout order, migration strategy, feature flags
- Library, dependency, or tooling choices

**Read whatever you need during the grill.** `grilling`'s explore-before-asking rule applies in full here, **source files included**. The WHAT/HOW line governs what lands in the ticket, not what you're allowed to read. If exploration turns up a HOW decision the ticket seems to need, that's a signal for `architect-ticket`, not a section to add here.

---

## Propose-and-confirm split

When the full WHAT-grill is complete, **you** decide whether this is one ticket or several. Do **not** ask the user upfront which it will be.

**Split** when the Spec spans separable user-visible concerns and each slice is independently demoable end-to-end. **Keep as one** when the behaviours interlock, so no slice ships without the others.

State your recommendation with brief reasoning, either "one ticket, no split" or "N sub-issues". Then **wait for confirmation or pushback** before moving on. If the user pushes back, iterate until they confirm. The sub-issue list itself is proposed under Publishing, once the parent is filed.

For the split path, read `subissue-splitting.md` and follow its vertical-slice rule and two-tier coverage check.

---

## Publishing

Follow `ticket-shapes.md`'s **publish loop** for every ticket, parent and sub alike, and its **native wiring** for parentage and blocking.

Before the first preview of each task ticket, judge it against `ticket-shapes.md`'s **effort criteria** and state the level you'd give it, `trivial`, `minor`, `medium`, or `major`, with one line naming the check that decided it. The user confirms or overrides. Sub-issues are judged one at a time, since a `major` parent can have a `minor` sub-issue.

For a split, publish **parent first**, so sub-issues have something to attach to:

1. Preview, approve, and publish the parent. Capture its number, URL, and numeric id.
2. **Propose the sub-issue list.** Show every sub-issue as title plus one-line scope, plus the proposed blocking edges in `X blocked by Y` form. Iterate with the user, adding, removing, renaming, re-scoping, and re-wiring, until they approve.
3. Re-run the two-tier coverage check on the approved list.
4. Publish each sub-issue in dependency order, one full publish loop each, wiring it to the parent as it lands.

---

## Handoff

Close by naming the next step for each published task ticket, by its effort level:

- **`minor`.** `/execute-ticket <N>`.
- **`trivial`.** Open an ordinary session with the ticket, let the agent make the change, and check what no test reaches before merging.
- **`medium`.** `/architect-ticket <N>`, then `/kanban-ci:launch`.
- **`major`.** `/architect-ticket <N>`, then `/implement-ticket` and `/refactor-ticket`.
