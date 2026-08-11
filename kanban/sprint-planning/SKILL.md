---
name: sprint-planning
description: Chart one sprint from project_plan.md as a GitHub-native map — breadth-first grill the sprint goal, publish every task/research/prototype ticket as a sub-issue with native blocking, then on re-run graduate newly-resolved tickets out of the fog. Middle link of the scrum chain: project-planning → sprint-planning → implementation-planning. Use when user says "sprint-planning", "chart sprint N", or "plan this sprint".
---

# sprint-planning

You are Opus in the main thread. All work in this skill is Opus-direct — no subagent dispatch.

Read `project_plan.md` at the consuming project's repo root, let the user pick a sprint, and turn its goal into a GitHub-native **map**: the sprint's `(N)` issue holds the destination and a running decision log, and its **tickets** — native GitHub sub-issues, typed `task` / `research` / `prototype` — are the actual work items, wired together with native blocking. Everything reachable now gets grilled and published in this session; anything not yet specifiable is written down as fog and revisited on a later run.

This skill owns every sprint-linked ticket end to end — `new-issue` is only for cold-start/standalone issues with no sprint. Invoke the `grilling` skill for interview mechanics throughout; this document only defines the agenda and ticket typing. It reads three bundled templates at runtime — do not assume their contents from this document:

- `template_sprint_issue.md` — the map body (Destination / Notes / Decisions so far / Not yet specified)
- `template_task_ticket.md` — deliverable ticket body (Goal / Acceptance criteria / Out of scope)
- `template_question_ticket.md` — research/prototype ticket body (Question only)

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

**If no arg was provided:** list all sprints with their goals and status markers, then ask the user to pick one.

Do not proceed until a sprint is selected.

---

## Step 3 — Detect mode: charting or graduating

Scan for an existing map issue for this sprint:

```
gh issue list --state all --limit 500 --json number,title
```

Parse the leading `(N)` token from each title.

- **No match** → **Charting mode** (Steps 4–9). This is the sprint's first sprint-planning run.
- **Match found** → **Graduating mode** (Step 10). The map already exists; this run looks for newly-resolved tickets and graduates fog.

---

## Charting mode

### Step 4 — Read the destination (read-only)

Read the selected `### Sprint N` block. Extract and display the sprint goal line. **The sprint goal is immutable** — it is the map's Destination. Never edit it; it was set by `project-planning`.

### Step 5 — Breadth-first grill

Grill the user (via the `grilling` skill) across the **whole sprint scope at once** — fan out, don't go deep on any one item yet. The goal is to surface every task the sprint needs, not to fully specify each one.

For each item that surfaces, classify it:

- **`task`** — a deliverable, ready to be spec'd now (goal and acceptance criteria are already clear enough to state).
- **`research`** — an open question blocking a later task (unknown API, library choice, unclear fact) that a separate session should resolve.
- **`prototype`** — needs a cheap concrete artifact (UI sketch, behavior stub) before it can be spec'd, via a separate `/prototype` session.
- **fog** — you can sense it's coming but can't state it precisely yet. Don't force it into a ticket. Write a loose one-line sketch instead.

Also propose **blocking edges**: which items can't be worked until another closes (e.g. a `task` blocked by a `research` question, or one `task` blocked by another). Propose this as part of the same pass, don't ask the user to enumerate dependencies from scratch.

**One-issue sizing** for `task` items: each should be a thin vertical slice, independently demoable as a single GitHub issue. Split anything bigger; merge anything that always ships together.

### Step 6 — Batch confirm gate

Show the user, together:

1. The full item list, each with its type (`task` / `research` / `prototype`) and one-line description.
2. The proposed blocking edges (`X blocked by Y`).
3. The fog sketch (items not yet ticketed).

Support natural-language edits — add an item, change its type, drop a blocking edge, retype a fog line into a real ticket or vice versa. Ask: **"Publish this batch?"** Do not create anything until the user confirms.

### Step 7 — Create the map issue

Render `template_sprint_issue.md`:

- **Destination** = the sprint goal (verbatim).
- **Notes** = domain pointers or standing preferences relevant to this sprint (keep short; empty is fine).
- **Decisions so far** = empty on first creation.
- **Not yet specified** = the confirmed fog sketch, one line per item.

```
gh issue create --title "(N) [sprint] <sprint name>" --body "$(cat ...rendered...)"
```

Note the issue number — every wiring call below needs the **numeric database id** of an issue, not its number. Get it with:

```
gh api repos/{owner}/{repo}/issues/<issue-number> --jq .id
```

### Step 8 — Publish tickets

**Research / prototype tickets** — for each, render `template_question_ticket.md` with the question filled in, then:

```
gh issue create --title "[research] <short title>" --body "$(cat ...rendered...)" --label "sprint:research"
```

(or `[prototype]` / `sprint:prototype`). No `(N.M)` id tag — these aren't implementation-plan targets. Publish the whole batch of these directly; no further per-item discussion.

**Task tickets** — process **one at a time**, sequentially. For each:

1. Draft the Goal and a short rationale for the proposed Acceptance criteria (and Out of scope) from what the breadth-first grill already surfaced. Fill `## Branch` too: a **2–4 word, kebab-case, no-article** slug derived from the title (`Add OAuth login for admin dashboard` → `oauth-admin-login`). Slug only — no issue number (it doesn't exist yet; `implementation-planning` prepends it), no `feature/` prefix.
2. Present the draft to the user; discuss and refine. The acceptance criteria carry the most weight here — spend the discussion on those, not on prose.
3. Assign the `(N.M)` id: read `project_plan.md`'s existing rows under `### Sprint N`, take `max(M) + 1` (start at 1 if none exist). Append-only — never renumber existing rows.
4. Publish:
   ```
   gh issue create --title "(N.M) [feature] <short title>" --body "$(cat ...rendered template_task_ticket.md...)" --label "sprint:task"
   ```
   Every task defaults to feature-shaped — do not ask feature vs bug here.
5. Move to the next task ticket.

**Wire sub-issue + blocking for every ticket published** (task, research, and prototype alike). Fetch each ticket's numeric id the same way as Step 7, then:

```
gh api repos/{owner}/{repo}/issues/<map-issue-number>/sub_issues -X POST -F sub_issue_id=<ticket-numeric-id>
```

For each confirmed blocking edge (`X blocked by Y`):

```
gh api repos/{owner}/{repo}/issues/<X-issue-number>/dependencies/blocked_by -X POST -F issue_id=<Y-numeric-id>
```

After the `gh` calls, surface the map issue URL and every ticket's URL to the user.

### Step 9 — Regenerate the plan's task-row table

`project_plan.md`'s per-sprint task table is a **synced view of GitHub, not hand-authored**. After publishing, list the map's current sub-issues:

```
gh api repos/{owner}/{repo}/issues/<map-issue-number>/sub_issues --jq '.[] | {number, title, state, labels: [.labels[].name]}'
```

Rebuild the `### Sprint N` task table from this list, one row per `task`-type ticket (filter on the `sprint:task` label):

```
| # | Task | Issue | Plan | Status |
|---|------|-------|------|:------:|
| N.M | <task title, stripped of id/type prefix> | #<issue-number> | — | ⬜ or ✅ (from issue state) |
```

`research`/`prototype` tickets are not rows in this table — they only exist as sub-issues of the map. Rewrite the whole table for this sprint; do not hand-edit individual cells (GitHub is the source of truth).

---

## Graduating mode (re-run on an existing map)

### Step 10 — Detect resolved tickets and graduate fog

1. List the map's sub-issues (same query as Step 9) and find any that are **closed** but not yet reflected in the map's Decisions so far section.
2. For each newly-closed ticket, read its closing comment/resolution, and append one line to **Decisions so far**:
   ```
   - [<ticket title>](<url>) — <one-line gist of the answer/outcome>
   ```
3. With these resolutions in hand, grill the user (via the `grilling` skill): **"Given this, what from Not yet specified is now specifiable?"** Fan out across the fog section only — not the whole sprint again.
4. Whatever graduates gets the same typing (`task` / `research` / `prototype`) and the same publish flow as Step 8 (including sub-issue + blocking wiring). Remove graduated lines from **Not yet specified**; anything still too vague stays in the fog.
5. Update the map issue body (`gh issue edit <N> --body "..."`) with the refreshed Decisions so far and Not yet specified sections.
6. Re-run Step 9 to refresh `project_plan.md`'s task-row table.

If nothing has closed since the last run, tell the user there's nothing to graduate yet and stop.

---

## Constraints

- **Never edit the sprint goal / Destination.** Read it, grill from it, never write to it.
- **Never resolve `research` or `prototype` tickets inline.** They're published open and picked up in their own separate sessions (a `/research` pass, a `/prototype` session). Sprint-planning only detects their closure on a later run.
- **Claim and frontier are out of scope for this skill.** Self-assigning a ticket and querying "what's pickable now" belongs to `implementation-planning`, at the point work actually begins — not here.
- **Append-only `(N.M)` numbering** for task tickets. Never renumber or delete existing rows on re-run.
- **`project_plan.md`'s task table is regenerated from GitHub, never hand-authored.** If GitHub and the plan ever disagree, GitHub wins.
- **Opus-direct.** No subagent dispatch.
- **The ticket names its own branch.** `template_task_ticket.md` carries a `## Branch` slug plus a standing footer; `implementation-planning` prepends the GitHub issue number so `review-edits` can link the work back. Fill the slug, and do not strip the footer, when refining task drafts in Step 8.
