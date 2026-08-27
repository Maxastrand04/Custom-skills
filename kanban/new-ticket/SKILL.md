---
name: new-ticket
description: Grill the user into a single-ticket spec covering WHAT, meaning behavior, scope, and acceptance criteria, and never HOW, meaning architecture and files. Publishes the spec as a GitHub Issue. If scope is too large, chains into a sub-issue split. Output feeds `implementation-planning`. For epic-linked work use `epic-planning` instead; this skill is for standalone tickets with no epic. Use when user wants to file a new ticket, capture a feature request or bug, says "new ticket", "create an issue", or "spec this out".
---

# new-ticket

Grill the user into a single, well-scoped GitHub ticket covering **WHAT** changes, meaning behavior, scope, and acceptance criteria, and never **HOW**, meaning architecture, files, and code. Publish via `gh`. Optionally split into vertical-slice sub-issues. Hand off to `/implementation-planning` for the HOW.

The published body is deliberately thin. The grill is not. Everything the grill surfaces must land as a **checkable acceptance criterion** or be consciously dropped. The criteria are this skill's real output, and they are what `implementation-planning` lifts.

Read the bundled files at runtime. Do not assume their contents from this document:

- **`ticket-shapes.md` is the single source of truth** for body shape, title format, labels, branch slug, the AI disclaimer, gh preflight, the publish loop, and native wiring. `epic-planning` reads the same file, which is why none of it is restated here. Read it before the first `gh` call.
- `subissue-splitting.md` holds the vertical-slice rule and the two-tier coverage check.

Run `ticket-shapes.md`'s **gh preflight** before any grilling.

---

## Invocation

Two modes:

1. **Cold start.** The user invokes with no extra text. Open with the first grill turn, feature vs bug.
2. **One-liner seed.** The user invokes with a short phrase such as "users can sign up with email". Treat that phrase as **the seed of the grill, not a finished ticket body.** It hints at the topic; every grill topic still runs.

If the user's phrase looks epic-linked, meaning it references an epic task, a `(N.M)` id, or `project_plan.md`, point them at `/epic-planning` instead. This skill does not resolve plan refs.

Do **not** synthesise a ticket from prior conversation context. The only inputs are the cold start and the one-liner seed.

---

## First grill turn, feature vs bug

The first question is always: **"Is this a feature or a bug?"** Ask once. Do not infer.

The answer picks the **grill agenda** below and the type prefix on the published title. It does **not** change the body shape or the label, since both feature and bug publish as a task ticket labelled `ticket:task`.

---

## Grill behavior, WHAT only

You are a developer grilling a product owner about product requirements. Invoke the `grilling` skill for the interview mechanics, and work the agenda one topic at a time.

**Feature agenda:**

1. Problem and motivation: the user-visible problem, and why now.
2. Target user or actor: who triggers or benefits.
3. Trigger or entry point: how the user reaches the behavior.
4. Expected behavior: the happy path end-to-end, from the user's side.
5. Edge cases and failure modes: missing, invalid, or conflicting inputs, and operations that can't complete.
6. Dependencies on existing functionality: behaviors this relies on or disturbs.
7. Out of scope: what might look related but isn't.

**Bug agenda:**

1. Symptom: what the user sees go wrong.
2. Reproduction steps: the minimal sequence that triggers it.
3. Expected vs actual, at the point of failure.
4. Scope of impact: who hits it, how often, and whether it blocks or annoys.
5. Conditions: user state, surface, and inputs under which it reproduces.
6. First seen or regression: always broken, or a regression from a known-good state.
7. Workarounds known: what users can do today, or "none known".
8. Out of scope: related bugs or refactors this fix won't touch.

**Drive every topic to a criterion.** For each answer, ask *"how would we know this is done?"* and write the observable condition. A topic that produces no criterion and no Out-of-scope line has left nothing in the ticket, so say so and resolve it before moving on. Bug tickets always carry two standing criteria: the reproduction steps no longer produce the symptom, and a regression test exists that would catch its return.

**Never settled in this ticket.** These are HOW topics, and they defer to `implementation-planning`:

- File paths, module names, function or class names, function signatures
- Schema design, database tables, API contract shapes
- Test framework choice, test file locations
- Rollout order, migration strategy, feature flags
- Library, dependency, or tooling choices

**Codebase exploration during grill: read whatever you need.** `grilling`'s explore-before-asking rule applies in full here, **source files included**. The **WHAT/HOW line is about what lands in the ticket, not about what you're allowed to read.** Reading source to understand current behavior is fine; recording the implementation you inferred from it is not. If exploration turns up a HOW decision the ticket seems to need, that's a signal for `implementation-planning`, not a section to add here.

---

## Propose-and-confirm split

When the full WHAT-grill is complete, **Claude evaluates** whether this is one ticket or several, using the criteria below. Do **not** ask the user upfront which it will be.

**Propose a split when:**

- Acceptance criteria span clearly separable user-visible concerns
- Each potential slice is independently demoable end-to-end
- Slices do not share so much state that they must ship together
- The change touches multiple distinct user flows or subsystems

**Keep as one ticket when:**

- It is a single coherent user-visible behavior change
- Acceptance criteria interlock, so no slice ships without the others
- It is naturally one vertical slice

State your recommendation with brief reasoning: either "one ticket, no split" or "N sub-issues" with each sub-issue's working title and one-line scope. Then **wait for confirmation or pushback** before moving on. If the user pushes back, iterate until they confirm.

For the split path, read `subissue-splitting.md` and follow its vertical-slice rule and two-tier coverage check.

---

## Publishing

Follow `ticket-shapes.md`'s **publish loop** for every ticket, parent and sub alike, and its **native wiring** for parentage and blocking.

For a split, publish **parent first**, so sub-issues have something to attach to:

1. Preview, approve, and publish the parent. Capture its number, URL, and numeric id.
2. **Propose the sub-issue list.** Show every sub-issue as title plus one-line scope, plus the proposed blocking edges in `X blocked by Y` form. Iterate with the user, adding, removing, renaming, re-scoping, and re-wiring, until they approve.
3. Re-run the two-tier coverage check on the approved list.
4. Publish each sub-issue in dependency order, one full publish loop each, wiring it to the parent as it lands.
