---
name: epic-planning
description: Chart one epic from project_plan.md as a GitHub-native map. Breadth-first grill the epic goal, publish every task, research, and prototype ticket as a sub-issue with native blocking, then on re-run graduate newly-resolved tickets out of the fog. Middle link of the kanban chain, running project-planning, then epic-planning, then implementation-planning. Use when user says "epic-planning", "chart epic N", or "plan this epic".
---

# epic-planning

You are Opus in the main thread. All work in this skill is Opus-direct, with no subagent dispatch.

Read `project_plan.md` at the consuming project's repo root, let the user pick an epic, and turn its goal into a GitHub-native **map**. The epic's `(N)` issue holds the destination and a running decision log, and its **tickets**, which are native GitHub sub-issues typed `task`, `research`, or `prototype`, are the actual work items, wired together with native blocking. Everything reachable now gets grilled and published in this session; anything not yet specifiable is written down as fog and revisited on a later run.

This skill owns every epic-linked ticket end to end. `new-ticket` is only for standalone tickets with no epic. Invoke the `grilling` skill for interview mechanics throughout; this document defines the agenda, the ticket typing, and the map, and nothing else.

Read these at runtime. Do not assume their contents from this document:

- **`../new-ticket/ticket-shapes.md` is the single source of truth** for ticket body shape, title format, labels, branch slug, the AI disclaimer, gh preflight, the publish loop, and native wiring. Read it before Step 1. Everything this skill publishes below the map issue follows it.
- `template_epic_issue.md` holds the map body, with Destination, Notes, Decisions so far, and Not yet specified. The map is not a ticket, so this template lives here.

---

## Input

Accept an optional epic number `N` as an argument, as in `/epic-planning 2`. If provided, use it. If absent, list the available epics interactively after loading the plan.

---

## Step 1: gh preflight

Run the **gh preflight** from `ticket-shapes.md`, including its remediation steps. Do not proceed until it passes or the `--repo` fallback is captured.

---

## Step 2: Load plan and select epic

Read `project_plan.md` at the project root.

If the file does not exist, stop and tell the user to run `/project-planning` first.

**If an epic number `N` was provided as an arg**, locate `### Epic N` in the plan. If it isn't found, list available epics and ask the user to pick.

**If no arg was provided**, list all epics with their goals and status markers, then ask the user to pick one.

Do not proceed until an epic is selected.

---

## Step 3: Detect mode, charting or graduating

Scan for an existing map issue for this epic:

```
gh issue list --state all --limit 500 --json number,title
```

Parse the leading `(N)` token from each title.

- **No match** means **charting mode**, Steps 4 through 9. This is the epic's first epic-planning run.
- **Match found** means **graduating mode**, Step 10. The map already exists, so this run looks for newly-resolved tickets and graduates fog.

---

## Charting mode

### Step 4: Read the destination, read-only

Read the selected `### Epic N` block. Extract and display the epic goal line. **The epic goal is immutable.** It is the map's Destination. Never edit it; it was set by `project-planning`.

### Step 5: Breadth-first grill

Grill the user, via the `grilling` skill, across the **whole epic scope at once**. Fan out, and don't go deep on any one item yet. The goal is to surface every task the epic needs, not to fully specify each one.

For each item that surfaces, classify it:

- **`task`.** A deliverable, ready to be spec'd now, meaning its goal and acceptance criteria are already clear enough to state.
- **`research`.** An open question blocking a later task, such as an unknown API, a library choice, or an unclear fact, that a separate session should resolve.
- **`prototype`.** Needs a cheap concrete artifact, such as a UI sketch or a behavior stub, before it can be spec'd, via a separate `/prototype` session.
- **fog.** You can sense it's coming but can't state it precisely yet. Don't force it into a ticket. Write a loose one-line sketch instead.

Also propose **blocking edges**, meaning which items can't be worked until another closes, such as a `task` blocked by a `research` question, or one `task` blocked by another. Propose this as part of the same pass, and don't ask the user to enumerate dependencies from scratch.

**One-issue sizing** for `task` items: each should be a thin vertical slice, independently demoable as a single GitHub issue. Split anything bigger, and merge anything that always ships together.

### Step 6: Batch confirm gate

Show the user, together:

1. The full item list, each with its type, meaning `task`, `research`, or `prototype`, and a one-line description.
2. The proposed blocking edges, in `X blocked by Y` form.
3. The fog sketch, meaning items not yet ticketed.

Support natural-language edits, such as adding an item, changing its type, dropping a blocking edge, or retyping a fog line into a real ticket or the reverse. Ask: **"Publish this batch?"** Do not create anything until the user confirms.

### Step 7: Create the map issue

Render `template_epic_issue.md`:

- **Destination** is the epic goal, verbatim.
- **Notes** are domain pointers or standing preferences relevant to this epic. Keep it short; empty is fine.
- **Decisions so far** is empty on first creation.
- **Not yet specified** is the confirmed fog sketch, one line per item.

```
gh issue create --title "(N) [epic] <epic name>" --body "$(cat ...rendered...)"
```

Capture its issue number and its numeric database id, per `ticket-shapes.md`. Every wiring call below needs the id.

### Step 8: Publish tickets

Every ticket here uses `ticket-shapes.md`'s shapes, titles, labels, and publish loop. Epic tickets take the `epic:` label scope, so `epic:task`, `epic:research`, and `epic:prototype`.

**Research and prototype tickets** use the question ticket shape. Publish the whole batch directly, with no further per-item discussion, since the question was already agreed at the Step 6 gate.

**Task tickets** use the task ticket shape and are processed **one at a time**, sequentially. For each:

1. Draft the Goal, the Acceptance criteria, the Out of scope, and the Branch slug from what the breadth-first grill already surfaced.
2. Run the publish loop's preview and edit cycle. The acceptance criteria carry the most weight, so spend the discussion on those, not on prose.
3. Assign the `(N.M)` id by reading `project_plan.md`'s existing rows under `### Epic N` and taking `max(M) + 1`, starting at 1 if none exist. This is append-only. Never renumber existing rows.
4. Publish with the title `(N.M) [feature] <short title>`. Every task defaults to feature-shaped, so do not ask feature vs bug here.
5. Move to the next task ticket.

**Wire every published ticket** as a sub-issue of the map, and wire each confirmed blocking edge, per `ticket-shapes.md`'s native wiring. This covers task, research, and prototype alike.

### Step 9: Regenerate the plan's task-row table

`project_plan.md`'s per-epic task table is a **synced view of GitHub, not hand-authored**. After publishing, list the map's current sub-issues:

```
gh api repos/{owner}/{repo}/issues/<map-issue-number>/sub_issues --jq '.[] | {number, title, state, labels: [.labels[].name]}'
```

Rebuild the `### Epic N` task table from this list, one row per `task`-type ticket, filtering on the `epic:task` label:

```
| # | Task | Issue | Plan | Status |
|---|------|-------|------|:------:|
| N.M | <task title, stripped of id and type prefix> | #<issue-number> | TBD | ⬜ or ✅, from issue state |
```

`research` and `prototype` tickets are not rows in this table. They only exist as sub-issues of the map. Rewrite the whole table for this epic, and do not hand-edit individual cells, since GitHub is the source of truth.

---

## Graduating mode, a re-run on an existing map

### Step 10: Detect resolved tickets and graduate fog

1. List the map's sub-issues, using the same query as Step 9, and find any that are **closed** but not yet reflected in the map's Decisions so far section.
2. For each newly-closed ticket, read its closing comment or resolution, and append one line to **Decisions so far**:
   ```
   - [<ticket title>](<url>): <one-line gist of the answer or outcome>
   ```
3. With these resolutions in hand, grill the user, via the `grilling` skill, on this question: **"Given this, what from Not yet specified is now specifiable?"** Fan out across the fog section only, not the whole epic again.
4. Whatever graduates gets the same typing, meaning `task`, `research`, or `prototype`, and the same publish flow as Step 8, including sub-issue and blocking wiring. Remove graduated lines from **Not yet specified**; anything still too vague stays in the fog.
5. Update the map issue body with `gh issue edit <N> --body "..."`, carrying the refreshed Decisions so far and Not yet specified sections.
6. Re-run Step 9 to refresh `project_plan.md`'s task-row table.

If nothing has closed since the last run, tell the user there's nothing to graduate yet and stop.

---

## Constraints

- **Never edit the epic goal or Destination.** Read it, grill from it, never write to it.
- **Never resolve `research` or `prototype` tickets inline.** They're published open and picked up in their own separate sessions, such as a `/prototype` session. Epic-planning only detects their closure on a later run.
- **Claim and frontier are out of scope for this skill.** Self-assigning a ticket and querying "what's pickable now" belongs to `implementation-planning`, at the point work actually begins.
- **Append-only `(N.M)` numbering** for task tickets. Never renumber or delete existing rows on re-run.
- **`project_plan.md`'s task table is regenerated from GitHub, never hand-authored.** If GitHub and the plan ever disagree, GitHub wins.
- **Opus-direct.** No subagent dispatch.
