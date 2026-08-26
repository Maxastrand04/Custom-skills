---
name: project-planning
description: Run an epic-roadmap planning session inside an existing git repo. Adaptively grill to mutual understanding, propose vertical-slice epics each with an epic goal, then write/update CONTEXT.md and project_plan.md. Use when user says "project-planning", "plan this project", "roadmap", or "set up a project plan". For breaking one epic into tasks, use `epic-planning` instead.
---

# project-planning

You are Opus in the main thread, driving a roadmap-level planning session inside an existing git repo. All work in this skill is Opus-direct, with no subagent dispatch.

See `CONTEXT.md` at this repo's root for the canonical Language section structure that the project's own `CONTEXT.md` must mirror.

---

## Input

The skill is invoked with an optional one-sentence project seed. If none was provided and no `CONTEXT.md` or `project_plan.md` exists, ask the user for one, since a single sentence is enough, before doing anything else. If existing artifacts are present, the seed is unnecessary; skip this step.

---

## Git-repo guard

Before doing anything else, run:

```
git rev-parse --is-inside-work-tree
```

If the command fails (non-zero exit), print exactly:

> `project-planning must be run inside a git repository. Exiting, no files written.`

Then **stop immediately. Write nothing.**

---

## Sync epic status from GitHub

Before the grill, if `project_plan.md` exists, refresh each epic's status marker from GitHub:

```
gh issue list --state all --limit 500 --json number,title,state
```

Parse the leading `(N)` token from each title. For every epic whose `(N)` issue is found, a `state` of `CLOSED` gives `✅`, and a `state` of `OPEN` keeps `🟡` if the epic already has any published sub-issue tasks and otherwise gives `⬜`. Write the refreshed markers back into `project_plan.md`'s `### Epic N: ... <marker>` heading lines before continuing. Epics with no matching `(N)` issue yet are left as `⬜`, meaning not yet charted.

This sync only touches the epic-level status marker in each heading. It never touches epic goals, scope, or the per-epic task tables, which are `epic-planning`'s responsibility and get regenerated when it runs.

If `gh` is unavailable or unauthenticated, skip this step silently and proceed with whatever `project_plan.md` already has. This sync is a freshness nicety, not a hard requirement for `project-planning` to run.

---

## Adaptive grill

Invoke the `grilling` skill for the interview mechanics; this section supplies only the agenda and its termination condition.

**Read first.** Before asking anything, read `CONTEXT.md` and `project_plan.md` at the project root if they exist (post-sync, if the sync above ran). Summarize your current understanding back to the user in two to four sentences: what the project is, who it's for, what's already planned, and what's already done (completed epics). Be explicit about what you do and do not yet know.

**Ask only on gaps.** Do not run a fixed N-question script. Ask only where understanding is genuinely absent or unclear; if the existing artifacts already answer an area, do not re-ask it.

Areas to cover (ask only where gaps remain):

1. **Problem statement.** What is this project solving?
2. **Primary user or consumer.** Who uses it?
3. **Success criteria.** One observable behavior that defines done.
4. **Scope boundaries.** What is explicitly out of scope?
5. **Domain language.** 3-6 nouns that recur in code and UI.

**Termination.** Stop the grill once you can fill in all five areas. Announce:

> `Understanding captured. Proposing epic breakdown.`

Proceed directly to Epic breakdown.

---

## Epic breakdown

Propose an epic breakdown as a numbered list. Each epic must have:

- An epic number `(N)`, as in `Epic 1`
- A one-sentence **epic goal**, meaning the observable outcome at the end of the epic
- A status marker, which is `⬜ Not started` for all new epics

Epics are **vertical slices**. Each delivers working, demonstrable functionality end-to-end, not a horizontal layer. Don't make "Epic 1 = backend" and "Epic 2 = frontend".

**Completed epics (✅) from an existing plan are listed at the top and are immutable.** Do not re-propose or modify them. Only propose new epics after the last completed one.

After proposing the breakdown, ask:

> `Does this epic breakdown look right? Confirm to write, or tell me what to change.`

**Wait for explicit user confirmation before writing any file.** This is the confirm gate, and no writes happen before it.

---

## Write artifacts

On confirmation, write or update the following. Never create new files outside this list.

### CONTEXT.md

If `CONTEXT.md` does not exist, create it at the project root mirroring the **Language and Relationships** structure of this repo's own `CONTEXT.md`. Read that file first: it holds `**Term**:` blocks with `_Avoid_:` lines, plus a Relationships bullet list.

If `CONTEXT.md` already exists, update it in place: add or revise Language entries and Relationships bullets to reflect the current domain understanding. Match the existing style exactly.

### project_plan.md

Read `./template_project_plan.md`, a skill-relative path, and use it as the structural contract. Write or update `project_plan.md` at the **consuming project's repo root**, meaning the working directory, not this skill's directory.

**Re-run immutability:** if `project_plan.md` already exists, read it first. Any epic marked `✅` must be reproduced verbatim, with goal, scope, and tasks unchanged. Only append new epics or revise goals and out-of-scope content for non-completed epics.

Leave the Directory tree section with this placeholder. Nothing populates it:

> `[Directory tree: not populated]`

Output both file paths as clickable markdown links after writing.

---

## Constraints

- No git init, no `gh repo create`, no safety-rail preflight. This skill assumes an existing git repo, enforced by the guard above.
- No artifact scaffolding, meaning no README, no `.gitignore`, no CLAUDE.md, and no license file. Those belong to a scaffolding skill.
- No per-task slicing. Epics contain a tasks placeholder owned by `epic-planning`. Do not break epics into individual issues here. Defer that entirely to `epic-planning`.
- No subagent dispatch. Every action is Opus-direct.
- Do not read, write, or access files inside `claude_ignore/`.

---

## Delegation rules

**All work in this skill is Opus-direct.** No `claude` implementer subagents. No `Explore` tester subagents. No `general-purpose` dispatch.

The work is conversation and file edits only, and a subagent round-trip buys nothing here.
