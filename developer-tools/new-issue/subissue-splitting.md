<!-- Inspired by the tracer-bullet split rule in the `to-issues` skill. -->

# Sub-issue splitting guide

Use this guide when a parent issue is large enough that Claude proposes a multi-plan split. It defines how to slice the parent into sub-issues that can each ship on their own and that, together, cover everything the parent promised.

## Vertical-slice rule

Each sub-issue must be a **vertical slice** — an end-to-end, demoable change from the user's point of view. A slice delivers a real behavior the user can see, not a layer of internals.

- Good: "User can sign up with email" (touches whatever it needs to, end-to-end).
- Bad: "Add the database table", "Add the API endpoint", "Add the form" — these are horizontal layers, not slices. None of them is demoable on its own.

If a proposed sub-issue cannot be demoed end-to-end without one of the others shipping first as a hard prerequisite of *the same behavior*, it is probably a layer, not a slice. Either merge it back into the parent or restructure the split.

## Sub-issue body template

Every sub-issue body uses `template_issue.md` — the same shape as the parent: `## Goal`, `## Acceptance criteria`, `## Out of scope`, with the AI-disclaimer block as the first line.

Fill the template per sub-issue:
- **Goal** describes the slice end-to-end at behavior level — no file paths, no code.
- **Acceptance criteria** are observable conditions specific to this slice.
- **Out of scope** names the neighbouring slices this one does not deliver.

Parentage and blocking are **not** body sections — they are wired natively via the GitHub API (see *Native wiring* in `SKILL.md`).

## Dependency-order publishing

Publish sub-issues in **dependency order**, so that when a blocking edge is wired, the issue it points at already exists.

- Start with sub-issues that have no blockers.
- Publish each next sub-issue only after every sub-issue it is blocked by has been published, then POST its blocking edges.
- If a cycle appears in the proposed blocking graph, the split is wrong — go back and re-slice until the graph is acyclic.

## Two-tier coverage check

Before publishing any sub-issues, run a **two-tier coverage check**. Both tiers must pass.

### Tier 1 — Per-slice coverage

For each sub-issue on its own:
- Every acceptance criterion in that sub-issue is about behavior that belongs to this slice.
- The sub-issue's own acceptance criteria fully cover the slice it claims to deliver — nothing inside the slice is left unchecked.

A sub-issue that lists criteria belonging to a different slice, or that under-specifies its own slice, fails Tier 1.

### Tier 2 — Systemic coverage

Across the whole set of sub-issues:
- The **union** of all sub-issue acceptance criteria covers the **full** acceptance criteria of the parent issue.
- No parent criterion falls through the cracks between slices.
- No parent criterion is silently dropped because it didn't fit neatly into any one slice.

If Tier 2 fails, either expand an existing sub-issue, add a new sub-issue to absorb the gap, or pull the missing criterion back into the parent and re-evaluate whether the split still makes sense.

Only after both tiers pass does the split get published.
