---
name: sprint-planning
description: Take one sprint from project_plan.md, slice its goal into caveman-style (N.M) tasks written under that sprint, and create the sprint's parent (N) GitHub issue. Middle link of the scrum chain: project-planning → sprint-planning → new-issue. Use when user says "sprint-planning", "plan this sprint", "break down sprint N", or "create tasks for sprint N".
---

# sprint-planning

You are Opus in the main thread. All work in this skill is Opus-direct — no subagent dispatch.

Read `project_plan.md` at the consuming project's repo root, let the user pick a sprint, slice its goal into caveman-style task rows, write them into the plan, and create (or update) the sprint's parent `(N)` GitHub issue.

---

## Input

Accept an optional sprint number `N` as an argument (e.g. `/sprint-planning 2`). If provided, use it. If absent, list the available sprints interactively after loading the plan.

---

## Step 1 — gh preflight

Before reading the plan, confirm `gh` is installed, authenticated, and pointed at a real repo. Run, in order:

1. `gh --version`
2. `gh auth status`
3. `gh repo view`

Remediation:

- **`gh --version` fails** — `gh` is not installed. On macOS: `brew install gh`. Other platforms: https://cli.github.com/. Stop and wait.
- **`gh auth status` fails** — run `gh auth login` and wait for confirmation before proceeding.
- **`gh repo view` fails** — ask the user which repo to file the issue against, capture `owner/name`, and pass `--repo owner/name` to every subsequent `gh` call in this session.

Do not proceed until preflight passes (or the `--repo` fallback is captured).

---

## Step 2 — Load plan and select sprint

Read `project_plan.md` at the project root.

If the file does not exist, stop and tell the user to run `/project-planning` first.

**If a sprint number `N` was provided as an arg:** locate `### Sprint N` in the plan. If not found, list available sprints and ask the user to pick.

**If no arg was provided:** list all sprints with their goals and status markers, then ask the user to pick one. Example output:

```
Available sprints:
  Sprint 1 — Auth backend ✅
  Sprint 2 — Dashboard UI ⬜
  Sprint 3 — Export feature ⬜

Which sprint do you want to plan?
```

Do not proceed until a sprint is selected.

---

## Step 3 — Read sprint goal (read-only)

Read the selected `### Sprint N` block. Extract and display the sprint goal line.

**The sprint goal is immutable.** Never edit it. The goal line is the input to task slicing — not a target for revision.

---

## Step 4 — Slice into caveman tasks

Generate a proposed list of tasks that collectively deliver the sprint goal.

**Caveman task format:** each task is a short, direct description of one concrete deliverable — not a user story ("as a user…"). Use simple imperative language.

Example of good caveman tasks:
- `create a login endpoint that accepts email + password and returns a JWT`
- `add a logout button to the nav bar that clears the session`
- `write a migration that adds the users table with email, hashed_password, created_at`

**One-issue sizing:** each task should be a thin vertical slice that is independently demoable as a single GitHub issue. If a task would take more than a day or two to implement, split it. If two tasks always ship together, merge them.

**`(N.M)` append-only numbering:** read the sprint block for any existing task rows. Find the maximum existing M under sprint N. Start new tasks from `max(M) + 1`. If no tasks exist yet, start at 1. Never renumber or delete existing task rows.

Show the proposed task list to the user for review before writing anything. Support natural-language edits ("add a task for X", "split task 2", "drop task 3").

---

## Step 5 — Preview and confirm gate

Before writing anything, show:

1. **Task rows** to be appended — formatted as the table rows that will be written:

   ```
   | N.M | task description | — | — | ⬜ |
   ```

2. **Parent issue body** — rendered from `template_sprint_issue.md` with the sprint goal and task checklist filled in.

Ask for explicit confirmation: **"Write tasks to the plan and create/update the (N) issue?"**

Do not write anything until the user confirms. Support inline edits during preview — re-render after each edit.

---

## Step 6 — Write task rows to plan

After confirmation, write the task rows into the `### Sprint N` block in `project_plan.md`.

The sprint's task table uses this header and row format:

```
| # | Task | Issue | Plan | Status |
|---|------|-------|------|:------:|
| N.M | task description | — | — | ⬜ |
```

If the header row already exists, append only the new task rows below any existing rows. If the header does not yet exist (empty sprint placeholder), write the full header + rows.

**The plan is the source of truth.** Write the plan before creating the issue. Do not roll back the plan write if the `gh` call fails — surface the error and let the user retry the issue step.

---

## Step 7 — Create or update parent `(N)` issue

Detect whether a `(N) [feature]` issue for this sprint already exists:

```
gh issue list --state all --limit 500 --json number,title
```

(Add `--repo owner/name` if the preflight fallback captured one.)

Parse the leading `(N)` token from each title. Look for an exact match on the sprint number N.

**If no match:** create the issue.

```
gh issue create \
  --title "(N) [feature] <sprint name>" \
  --body "$(cat sprint-planning/template_sprint_issue.md | ...rendered body...)"
```

The title uses the sprint number N from the **plan** — not `max+1` from existing issues. The `<sprint name>` is the sprint's short name from the plan heading (e.g. `(2) [feature] Dashboard UI`).

**If a match exists:** update its body with the current task checklist.

```
gh issue edit <issue-number> --body "$(cat ...rendered body...)"
```

Render the issue body from `template_sprint_issue.md` (relative path — the template is in the same directory as this SKILL.md).

After the `gh` call, surface the issue URL to the user.

---

## Constraints

- **Never edit the sprint goal.** Read it, slice it, but never write to the goal line (AD-4).
- **Never call `new-issue`.** `(N.M)` sub-issues are filed later by `new-issue`; the Issue and Plan columns stay blank (`—`) at write time (AD-11).
- **Never auto-increment the sprint number** from existing GitHub issues. The title `(N)` must use the plan's sprint number (AD-8).
- **Append-only task rows.** Never renumber or delete existing `(N.M)` rows on re-run (AD-7).
- **Write order: plan first, then issue.** No rollback on `gh` failure (AD-9).
- **Opus-direct.** No subagent dispatch (AD-14).
