---
name: new-issue
description: Grill the user into a single-issue spec covering WHAT (behavior, scope, acceptance criteria) — not HOW (architecture, files). Publishes the spec as a GitHub Issue. If scope is too large, chains into a local sub-issue split. Output feeds `implementation-planning`. For sprint-linked work use `sprint-planning` instead — this skill is for standalone issues with no sprint. Use when user wants to create a new issue, file a feature request, capture a new functionality, says "new issue", "create an issue", or "spec this out".
---

# new-issue

Grill the user into a single, well-scoped GitHub Issue covering **WHAT** changes (behavior, scope, acceptance criteria) — never **HOW** (architecture, files, code). Publish via `gh`. Optionally split into vertical-slice sub-issues. Hand off to `/implementation-planning` for the HOW.

The published body is deliberately thin — **Goal / Acceptance criteria / Out of scope**, the same ticket shape `sprint-planning` publishes. The grill is not thin. Everything the grill surfaces must land as a **checkable acceptance criterion** or be consciously dropped: the criteria are this skill's real output, and they are what `implementation-planning` lifts.

This skill is markdown-only orchestration. Read the two bundled files at runtime — do not assume their contents from this document:

- `template_issue.md` — the one body template, used for every issue: standalone, parent, and sub
- `subissue-splitting.md` — vertical-slice rule, dependency-order publishing, two-tier coverage check

---

## Invocation

Accept two modes:

1. **Cold start** — user invokes the skill with no extra text. Open with the first grill turn (feature vs bug).
2. **One-liner seed** — user invokes with a short phrase (e.g. "users can sign up with email"). Treat that phrase as **the seed of the grill, not a finished issue body.** It hints at the topic; every grill topic still runs.

If the user's phrase looks sprint-linked (references a sprint task, a `(N.M)` id, or `project_plan.md`), point them at `/sprint-planning` instead — this skill does not resolve plan refs.

Do **not** synthesise an issue from prior conversation context. Unlike `to-prd`, this skill starts fresh: the only inputs are the cold start or one-liner seed.

---

## gh preflight

Before any grill, confirm `gh` is installed, authenticated, and pointed at a real repo. Run, in order:

1. `gh --version`
2. `gh auth status`
3. `gh repo view`

Remediation, step by step:

- **`gh --version` fails** — `gh` is not installed. On macOS, point the user at `brew install gh`. On other platforms, point at https://cli.github.com/. Stop and wait for the user to install before proceeding.
- **`gh auth status` fails** — `gh` is installed but not authenticated. Tell the user to run `gh auth login` and wait for them to confirm before proceeding.
- **`gh repo view` fails** — either the current directory is not a git repo with a GitHub remote, or `gh` cannot resolve one. Fall back to the `--repo owner/name` flag: ask the user which repo to file the issue against, capture `owner/name`, and pass `--repo owner/name` to every subsequent `gh` call in this session.

Do not start grilling until preflight passes (or the `--repo` fallback is captured).

---

## First grill turn — feature vs bug

The first question is always: **"Is this a feature or a bug?"** Ask the user once. Do not infer.

The answer picks the **grill agenda** below and the type prefix / label on the published issue. It does **not** change the body shape — feature and bug issues both publish as `template_issue.md`.

---

## Grill behavior — WHAT only

You are a developer grilling a product owner about product requirements. Invoke the `grilling` skill for the interview mechanics; work the agenda one topic at a time.

**Feature agenda:**

1. Problem & motivation — the user-visible problem, and why now.
2. Target user / actor — who triggers or benefits.
3. Trigger / entry point — how the user reaches the behavior.
4. Expected behavior — the happy path end-to-end, from the user's side.
5. Edge cases & failure modes — missing, invalid, or conflicting inputs; operations that can't complete.
6. Dependencies on existing functionality — behaviors this relies on or disturbs.
7. Out of scope — what might look related but isn't.

**Bug agenda:**

1. Symptom — what the user sees go wrong.
2. Reproduction steps — the minimal sequence that triggers it.
3. Expected vs actual — at the point of failure.
4. Scope of impact — who hits it, how often, blocking or annoyance.
5. Conditions — user state, surface, and inputs under which it reproduces.
6. First seen / regression — always broken, or a regression from a known-good state.
7. Workarounds known — what users can do today, or "none known".
8. Out of scope — related bugs or refactors this fix won't touch.

**Drive every topic to a criterion.** For each answer, ask *"how would we know this is done?"* and write the observable condition. A topic that produces no criterion and no Out-of-scope line has left nothing in the issue — say so and resolve it before moving on. Bug issues always carry two standing criteria: the reproduction steps no longer produce the symptom, and a regression test exists that would catch its return.

**Never settled in this issue (HOW topics — defer to `implementation-planning`):**

- File paths, module names, function or class names, function signatures
- Schema design, database tables, API contract shapes
- Test framework choice, test file locations
- Rollout order, migration strategy, feature flags
- Library, dependency, or tooling choices

**Codebase exploration during grill — read whatever you need.** Read `CONTEXT.md`, `README.md`, ADRs under `docs/adr/`, and **source files** freely, as much as the issue calls for. You decide what is worth reading; a feature that touches existing behavior, or a bug whose symptom is unclear, is usually better spec'd after looking at the code. Exploration serves the grill: it makes questions sharper, grounds the issue in the project's real language and existing behavior, and stops you asking the user things the repo already answers.

The **WHAT/HOW line is about what lands in the issue, not about what you're allowed to read.** Reading source to understand current behavior is fine; recording the implementation you inferred from it is not. If exploration turns up a HOW decision the issue seems to need, that's a signal for `implementation-planning`, not a section to add here.

---

## Propose-and-confirm split

When the full WHAT-grill is complete, **Claude evaluates** whether this is one issue or several, using the criteria below. Do **not** ask the user upfront which it will be.

**Propose a multi-plan split when:**

- Acceptance criteria span clearly separable user-visible concerns
- Each potential slice is independently demoable end-to-end
- Slices do not share so much state that they must ship together
- The change touches multiple distinct user flows or subsystems

**Keep as one plan when:**

- It is a single coherent user-visible behavior change
- Acceptance criteria interlock — no slice ships without the others
- It is naturally one vertical slice

State your recommendation clearly, with brief reasoning: either "one issue, no split" or "N sub-issues" with each sub-issue's working title and one-line scope. Then **wait for user confirmation or pushback** before moving on. If the user pushes back, iterate on the proposal until they confirm.

For the multi-plan path, read `subissue-splitting.md` and follow its vertical-slice rule, dependency-order publishing, and two-tier coverage check.

### Two-tier coverage rule (multi-plan only)

Before publishing any sub-issues, both tiers must hold:

- **Tier 1 — per-slice coverage.** Each sub-issue's acceptance criteria fully cover the slice it claims to deliver. No criterion in a sub-issue belongs to a different slice; no part of the slice is left unchecked.
- **Tier 2 — systemic coverage.** The **union** of all sub-issue acceptance criteria covers the **full** acceptance criteria of the parent issue. Nothing the parent promised is dropped between slices.

If either tier fails, restructure the split (expand a sub-issue, add a sub-issue, or pull the missing criterion back into the parent) before publishing.

---

## Preview, inline edits, publish

Every issue — parent and sub — goes through the same loop: **preview, edit, approve, publish.**

1. **Preview rendered title + body** as the chat message. Show the full title (with the `[feature]` / `[bug]` prefix) and the full body markdown rendered from `template_issue.md`. The user sees the rendered issue body before any `gh` call. A fenced code block is acceptable if it helps readability.
2. **Support natural-language inline edits** — e.g. "rename criterion 3 to X", "drop the Out of scope bullet about Y", "tighten the goal sentence". Apply the edit, re-render the full title + body, and offer the next edit cycle.
3. **Publish only after explicit user approval.** "Looks good, publish it" or equivalent. Never assume approval; never publish silently.

```
gh issue create --title "[feature] <short title>" --body "$(cat ...rendered...)" --label "issue:feature"
```

(or `[bug]` / `issue:bug`.) The label must exist before use — create both idempotently once per session:

```
gh label create issue:feature --color 1D76DB || true
gh label create issue:bug --color D73A4A || true
```

After publish, capture the issue number and URL from the `gh` output, plus its **numeric database id** — every wiring call below needs the id, not the number:

```
gh api repos/{owner}/{repo}/issues/<issue-number> --jq .id
```

---

## Multi-plan publish order

When the user approved a multi-plan split, publish in this strict order so that blocking edges reference issues that already exist:

1. **Parent first.** Preview parent title + body → user approves → `gh issue create` → capture the parent's issue number, URL, and numeric id.
2. **Propose the sub-issue list.** Show every sub-issue as title + one-line scope, plus the proposed blocking edges (`X blocked by Y`). Iterate with the user — add, remove, rename, re-scope, re-wire — until they approve the list.
3. **Publish each sub-issue in dependency order.** For each: render `template_issue.md`, preview, accept inline edits, get explicit approval, then `gh issue create` with the parent's type prefix and label. Start with sub-issues that have no blockers; only publish a sub-issue after every sub-issue it is blocked by has been published.

Re-run the two-tier coverage check on the final approved list before the first sub-issue gets published.

### Native wiring

Parentage and blocking are **GitHub-native, never body text**. After each sub-issue is published, attach it to the parent:

```
gh api repos/{owner}/{repo}/issues/<parent-issue-number>/sub_issues -X POST -F sub_issue_id=<sub-numeric-id>
```

For each confirmed blocking edge (`X blocked by Y`):

```
gh api repos/{owner}/{repo}/issues/<X-issue-number>/dependencies/blocked_by -X POST -F issue_id=<Y-numeric-id>
```

After the `gh` calls, surface the parent issue URL and every sub-issue URL to the user.

---

## Issue title format

- `[feature] short title` or `[bug] short title`
- **No `(N)` id tag.** The GitHub issue number is the sole identifier — `implementation-planning` names its plan file after it (`42_<slug>.md`).
- Bracketed type prefix is **lowercase** and comes first.
- Title cap is **70 characters total** (type prefix + title).
- **Sub-issues inherit the parent's type prefix and label.**
- **No `[parent]` marker.** Parent status is visible through GitHub's native sub-issue list.

---

## AI disclaimer

Every published issue body — parent and sub — starts with the disclaimer block:

```
> *This was generated by AI during a new-issue grill session.*
```

This is enforced by `template_issue.md`, so as long as you start from the template the disclaimer is already there. Do not strip it during inline edits.

The template also carries a standing **Branch naming** footer. Like the disclaimer, it is template-enforced — do not strip it during inline edits.

---

## Branch slug

**The issue names its own branch.** Fill `## Branch` on every issue — parent and sub — before the first preview; never leave it to `implementation-planning`.

- **2–4 words, kebab-case, no articles** — a slug describing what the issue delivers, derived from the title. `[feature] Add OAuth login for admin dashboard` → `oauth-admin-login`.
- **Slug only.** No issue number (it doesn't exist yet — `implementation-planning` prepends it), no `feature/` prefix, no type prefix.
- Show it in the preview and accept inline edits on it like any other section.
