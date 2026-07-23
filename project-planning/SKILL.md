---
name: project-planning
description: Run a sprint-roadmap planning session inside an existing git repo — adaptively grill to mutual understanding, propose vertical-slice sprints each with a sprint goal, then write/update CONTEXT.md and project_plan.md. Use when user says "project-planning", "plan this project", "roadmap", or "set up a project plan". For breaking one sprint into tasks, use `sprint-planning` instead.
---

# project-planning

You are Opus in the main thread, driving a roadmap-level planning session inside an existing git repo. All work in this skill is Opus-direct — no subagent dispatch.

See `CONTEXT.md` at this repo's root for the canonical Language section structure that the project's own `CONTEXT.md` must mirror.

---

## Input

The skill is invoked with an optional one-sentence project seed. If none was provided and no `CONTEXT.md` or `project_plan.md` exists, ask the user for one — a single sentence is enough — before doing anything else. If existing artifacts are present, the seed is unnecessary; skip this step.

---

## Git-repo guard

Before doing anything else, run:

```
git rev-parse --is-inside-work-tree
```

If the command fails (non-zero exit), print exactly:

> `project-planning must be run inside a git repository. Exiting — no files written.`

Then **stop immediately. Write nothing.**

---

## Sync sprint status from GitHub

Before the grill, if `project_plan.md` exists, refresh each sprint's status marker from GitHub:

```
gh issue list --state all --limit 500 --json number,title,state
```

Parse the leading `(N)` token from each title. For every sprint whose `(N)` issue is found: `state == CLOSED` → `✅`, `state == OPEN` → keep `🟡` if the sprint already has any published sub-issue tasks, otherwise `⬜`. Write the refreshed markers back into `project_plan.md`'s `### Sprint N — ... <marker>` heading lines before continuing. Sprints with no matching `(N)` issue yet are left as `⬜` (not yet charted).

This sync only touches the sprint-level status marker in each heading — it never touches sprint goals, scope, or the per-sprint task tables (those are `sprint-planning`'s responsibility, regenerated when it runs).

If `gh` is unavailable or unauthenticated, skip this step silently and proceed with whatever `project_plan.md` already has — this sync is a freshness nicety, not a hard requirement for `project-planning` to run.

---

## Adaptive grill

**Read first.** Before asking anything, check for existing artifacts:

1. Read `CONTEXT.md` at the project root if it exists.
2. Read `project_plan.md` at the project root if it exists (post-sync, if the sync above ran).

Summarize your current understanding back to the user in two to four sentences: what the project is, who it's for, what's already planned, and what's already done (completed sprints). Be explicit about what you do and do not yet know.

**Ask only on gaps.** Do not run a fixed N-question script. For each area where understanding is genuinely absent or unclear — problem statement, audience, success criteria, scope boundaries, domain language — ask one question at a time. Stop asking when you can articulate all five areas with confidence. If the existing artifacts already answer an area, do not re-ask it.

Areas to cover (ask only where gaps remain):

1. **Problem statement** — what is this project solving?
2. **Primary user / consumer** — who uses it?
3. **Success criteria** — one observable behavior that defines done.
4. **Scope boundaries** — what is explicitly out of scope?
5. **Domain language** — 3–6 nouns that recur in code and UI.

**Termination.** Stop the grill once you can fill in all five areas. Announce:

> `Understanding captured. Proposing sprint breakdown.`

Proceed directly to Sprint breakdown.

---

## Sprint breakdown

Propose a sprint breakdown as a numbered list. Each sprint must have:

- A sprint number `(N)` — e.g. `Sprint 1`
- A one-sentence **sprint goal** — the observable outcome at the end of the sprint
- A status marker: `⬜ Not started` for all new sprints

Sprints are **vertical slices** — each delivers working, demonstrable functionality end-to-end, not a horizontal layer (don't make "Sprint 1 = backend" + "Sprint 2 = frontend").

**Completed sprints (✅) from an existing plan are listed at the top and are immutable.** Do not re-propose or modify them. Only propose new sprints after the last completed one.

After proposing the breakdown, ask:

> `Does this sprint breakdown look right? Confirm to write, or tell me what to change.`

**Wait for explicit user confirmation before writing any file.** This is the confirm gate — no writes happen before it.

---

## Write artifacts

On confirmation, write or update the following. Never create new files outside this list.

### CONTEXT.md

If `CONTEXT.md` does not exist, create it at the project root mirroring the **Language + Relationships** structure of this repo's own `CONTEXT.md` (read it first: `**Term**:` blocks with `_Avoid_:` lines, plus a Relationships bullet list).

If `CONTEXT.md` already exists, update it in place: add or revise Language entries and Relationships bullets to reflect the current domain understanding. Match the existing style exactly.

### project_plan.md

Read `./template_project_plan.md` (skill-relative path) and use it as the structural contract. Write or update `project_plan.md` at the **consuming project's repo root** (the working directory, not this skill's directory).

**Re-run immutability:** if `project_plan.md` already exists, read it first. Any sprint marked `✅` must be reproduced verbatim — goal, scope, and tasks unchanged. Only append new sprints or revise goals and out-of-scope content for non-completed sprints.

After writing, invoke the `directory-tree` skill to regenerate the Directory tree section of `project_plan.md`. If the `directory-tree` skill is unavailable, leave the Directory tree section with this placeholder:

> `[Directory tree — run /directory-tree to populate this section]`

Output both file paths as clickable markdown links after writing.

---

## Constraints

- No git init, no `gh repo create`, no safety-rail preflight. This skill assumes an existing git repo (enforced by the guard above).
- No artifact scaffolding (no README, no `.gitignore`, no CLAUDE.md, no license file). Those belong to a scaffolding skill.
- No per-task slicing. Sprints contain a tasks placeholder owned by `sprint-planning`. Do not break sprints into individual issues here — defer that entirely to `sprint-planning`.
- No subagent dispatch. Every action is Opus-direct.
- Do not read, write, or access files inside `claude_ignore/`.

---

## Delegation rules

**All work in this skill is Opus-direct.** No `claude` implementer subagents. No `Explore` tester subagents. No `general-purpose` dispatch.

The work is conversation + file edits only — a subagent round-trip buys nothing here.
