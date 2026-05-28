---
name: project-setup
description: Scaffold a fresh project end-to-end — safety-check the working directory, init git + GitHub, grill the user into a `CONTEXT.md` alignment, then walk the bundled artifact checklist to populate every chosen scaffold file with real content. Use when user says "project-setup", "scaffold a project", "set up a new repo", or "start a new project".
---

# project-setup

You are Opus in the main thread, driving a one-shot scaffolding session that takes a working directory from empty (or near-empty) to a structured, committed, pushed project. All work in this skill is Opus-direct — no subagent dispatch.

See `CONTEXT.md` at this repo's root for the canonical Language section structure that the project's own `CONTEXT.md` must mirror.

---

## Input

The skill is invoked with an optional one-sentence project description. If none was provided, ask the user for one — a single sentence is enough — and wait for a reply before doing anything else.

A provided description becomes the **seed** for Session 1 question 1 (problem statement): propose it back for confirmation rather than re-asking from scratch.

---

## Safety-rail preflight

Detect the state of the current working directory before any write.

**Soft state — proceed silently:**
- `.git/` alone
- `README.md` alone
- dotfiles only (`.gitignore`, `.editorconfig`, etc.)
- empty source directories
- source files that contain only imports or placeholders

**Hard state — must triage:**
- `implementation_plans/` contains any `.md` file, **or**
- any source file contains non-trivial implementation (Claude reads the file and judges; if uncertain, ask the user before proceeding)

On hard state, use the harness's `AskUserQuestion` mechanism with **four options**:

1. **Proceed in place** — only recommend if contents are clearly not a project.
2. **Clear everything + restart** — list the exact paths first, require an explicit `yes, wipe` reply. Preserve `.git/` if the user requests.
3. **Cherry-pick removal** — list each path, user marks which to remove.
4. **Bail to subdirectory** — ask the user for a name, `mkdir`, `cd` into it.

Recommendation logic is indexed off detected state — e.g., a single stale `README.md` with one paragraph leans toward (1) or (3); a half-built source tree leans toward (4).

**Hard rule:** never auto-delete. Every removal requires an explicit user `yes` against a listed set of paths.

---

## Git + GitHub preflight

- If `.git/` is missing, run `git init`.
- Run `gh auth status`. If authenticated, run:

  ```
  gh repo create <basename> --private --source=. --remote=origin --push=false
  ```

  `<basename>` defaults to the basename of the current working directory; the user can override.
- If `gh` is missing or unauthenticated, fall back to local-only and tell the user to create the remote manually.

On success, emit one line:

- `Initialized git repo and created private GitHub repo: <url>` (gh path)
- `Initialized git repo. No GitHub remote — create one manually and run \`git remote add origin <url>\`.` (local-only path)

---

## Session 1 — Alignment grill

Five questions, **one per turn**, each including your recommendation and one-sentence reasoning. Fixed order:

1. **Problem statement** — what is this project solving? One sentence by default; accept a longer answer if the user volunteers more detail. Do not force terseness.
2. **Primary user / consumer** — who uses this?
3. **Success criteria** — one observable behavior that defines the v1 done-state.
4. **Scope boundaries** — what is explicitly **out** for v1?
5. **Domain language** — 3–6 nouns that will recur in code and UI.

**Termination.** After question 5, write the answers into `CONTEXT.md` at the project root, mirroring the **Language + Relationships** structure of this repo's own `CONTEXT.md` (read it first to copy the style — `**Term**:` blocks with `_Avoid_:` lines, plus a Relationships bullet list). Then announce verbatim:

> `Alignment captured in CONTEXT.md. Starting artifact grill.`

Proceed directly to Session 2 without waiting for further user prompt.

---

## Session 2 — Artifact grill

Before starting, read `./ARTIFACT_CHECKLIST.md` (skill-relative path) — it is the single source of truth for which artifact categories exist and what decisions each requires.

Silently filter categories that don't apply to the project shape inferred from `CONTEXT.md` (e.g., skip Database, Observability, and Containerization for a one-file script).

Walk the remaining categories in checklist order, **one question per turn**, each including a recommendation and one-sentence reasoning. `skip` is allowed per item; note the skip and move on.

**After each decision, immediately edit or create the affected file with real content** derived from `CONTEXT.md` and prior decisions. Never leave TODO stubs unless content genuinely depends on code that does not yet exist. Output the file path as a clickable markdown link after every edit.

### Per-file-type content rules

- **README.md** — real content, not skeleton. Pull problem, audience, and success criteria from `CONTEXT.md`; pull install/run/test commands from prior decisions.
- **Manifest files** (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`) — built incrementally as decisions accumulate; never overwrite a prior section, always append or amend the relevant table.
- **`.gitignore`** — fetched from the `github/gitignore` repo for the chosen language; append IDE entries (`.idea/`, `.vscode/`, `.DS_Store`).
- **LICENSE** — real text with current year and author name, not a placeholder template.
- **CLAUDE.md** — real stub encoding the convention **"1 implementation plan = 1 GitHub issue, close the issue when validation passes"**, linking to `CONTEXT.md` and `implementation_plans/`.
- **`implementation_plans/`** — directory only (no starter `.md` files inside; `plan-build` populates them later).
- **`project_plan.md`** (only if chosen in the Planning artifacts category) — populated from the bundled `./template_project_plan.md` via skill-relative path. Do not fetch from `~/.claude/templates/` or anywhere else.

---

## Final commit + push + report

Once the last relevant artifact decision is resolved:

1. `git add .`
2. `git commit -m "chore: scaffold project structure"`
3. `git push -u origin main` — skip if the project is local-only.

Then output the final report:

- **Line 1** — `Scaffolded <project-name> at <path>. Remote: <gh-url>.` (or `Scaffolded <project-name> at <path>. Local-only.` for the no-gh path).
- **Bulleted list** — every file created, each as a clickable markdown link (absolute path).
- **Line 3** — `Next: run /plan-build to plan the first slice.`

---

## Delegation rules

**All work in this skill is Opus-direct.** No `claude` implementer subagents. No `Explore` reviewer or tester subagents. No `general-purpose` dispatch.

The work is entirely conversation + file edits + shell commands — not production-code implementation — so the cost of a subagent round-trip outweighs any parallelism gain. This is the key distinction between `project-setup` and the test-first skills (`implement-tdd`, `plan-execute`), which delegate implementation precisely because production code benefits from a fresh-context implementer.

---

## Constraints

1. Do NOT auto-chain to `/plan-build` after the final report. The user invokes it themselves.
2. Do NOT auto-create `claude_ignore/`. It is an artifact-grill opt-in (default yes) inside the Claude-specific category.
3. Do NOT auto-create `project_plan.md`. It is an artifact-grill choice within the Planning artifacts category.
4. Do NOT push until the final commit. No intermediate pushes during the artifact grill.
5. Do NOT take destructive action (rm, wipe, overwrite an existing non-soft file) without an explicit user `yes` that listed the exact paths first.
6. Do NOT skip the safety-rail check on any invocation, even if the directory looks empty at a glance.
7. Do NOT read, write, edit, or access files inside `claude_ignore/` after the directory is created.
8. Do NOT write skeleton or `[TODO]` files when `CONTEXT.md` and prior decisions contain enough information to produce real content.
9. Do NOT dispatch subagents from this skill. Every action is Opus-direct.

---

## Reporting cadence

**Quiet on success.** One short line per phase boundary:

- `Preflight complete.`
- `Alignment captured.`
- `Artifact grill complete.`
- `Pushed initial commit.`

**On grill turns**, the question itself is the only output — no preamble, no recap.

**On escalation** (safety-rail trigger, `gh` unauthed, ambiguous source-file judgment, any branch where Opus needs the user to choose), state in plain English:

- What was detected.
- What the next prompt will be (or what fallback was taken).
