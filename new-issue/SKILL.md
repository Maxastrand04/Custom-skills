---
name: new-issue
description: Grill the user into a single-issue spec covering WHAT (behavior, scope, acceptance criteria) — not HOW (architecture, files). Publishes the spec as a GitHub Issue. If scope is too large, chains into a local sub-issue split. Output feeds `implementation-planning`. Use when user wants to create a new issue, file a feature request, capture a new functionality, says "new issue", "create an issue", or "spec this out".
---

# new-issue

Grill the user into a single, well-scoped GitHub Issue covering **WHAT** changes (behavior, scope, acceptance criteria) — never **HOW** (architecture, files, code). Publish via `gh`. Optionally split into vertical-slice sub-issues. Hand off to `/implementation-planning` for the HOW.

This skill is markdown-only orchestration. Read the four bundled files at runtime — do not assume their contents from this document:

- `template_feature_issue.md` — feature-path issue body template + grill topic list
- `template_bug_issue.md` — bug-path issue body template + grill topic list
- `template_subissue.md` — sub-issue body schema
- `subissue-splitting.md` — vertical-slice rule, dependency-order publishing, two-tier coverage check

---

## Invocation

Accept two modes — and only these two:

1. **Cold start** — user invokes the skill with no extra text. Open with the first grill turn (feature vs bug).
2. **One-liner seed** — user invokes with a short phrase (e.g. "users can sign up with email"). Treat that phrase as **the seed of the grill, not a finished issue body.** It hints at the topic; every grill topic still runs.

Do **not** synthesise an issue from prior conversation context. Unlike `to-prd`, this skill starts fresh: the only inputs are the cold start or the one-liner seed.

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

Based on the answer:

- **Feature** → read `template_feature_issue.md`. Use its section headings as the grill agenda.
- **Bug** → read `template_bug_issue.md`. Use its section headings as the grill agenda.

Read the template file at runtime. Do not paste its contents into chat; do not work from a remembered copy.

---

## Grill behavior — WHAT only

Work through every topic in the chosen template, one at a time. Ask focused, single-topic questions. Offer a recommended answer with brief reasoning when useful, but do not invent decisions the user has not made.

**Forbidden during grill (HOW topics — defer to `implementation-planning`):**

- File paths, module names, function or class names, function signatures
- Schema design, database tables, API contract shapes
- Test framework choice, test file locations
- Rollout order, migration strategy, feature flags
- Library, dependency, or tooling choices

**Codebase exploration during grill — vocabulary only.** You may read `CONTEXT.md`, `README.md`, and ADRs under `docs/adr/` (or the equivalent) for **domain glossary terms** so the issue body uses the project's language. Do **not** read source files during the grill. If a question would require reading source to answer, it is a HOW question — defer it.

---

## Propose-and-confirm split

When the full WHAT-grill is complete, **Claude evaluates** whether this is one issue or several, using the criteria below (from decisions §8). Do **not** ask the user upfront which it will be.

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

1. **Preview rendered title + body** as the chat message. Show the full title (with the `[feature]` or `[bug]` prefix) and the full body markdown. The user sees the rendered issue body before any `gh` call. A fenced code block is acceptable if it helps readability.
2. **Support natural-language inline edits** — e.g. "rename criterion 3 to X", "drop the Out of scope bullet about Y", "add a dependency on #42", "tighten the symptom sentence". Apply the edit, re-render the full title + body, and offer the next edit cycle.
3. **Run `gh issue create` only after explicit user approval.** "Looks good, publish it" or equivalent. Never assume approval; never publish silently.

After publish, capture the issue URL and ID from the `gh` output.

---

## Multi-plan publish order

When the user approved a multi-plan split, publish in this strict order so that `Blocked by` references resolve to real IDs:

1. **Parent first.** Preview parent title + body → user approves → `gh issue create` for the parent → capture the parent issue ID and URL.
2. **Propose the sub-issue list.** Show every sub-issue as title + one-line scope. Iterate with the user — add, remove, rename, re-scope — until they approve the list.
3. **Publish each sub-issue in dependency order.** For each sub-issue: render the body using `template_subissue.md` (with the parent link filled in and `Blocked by` referencing already-published sub-issue IDs), preview, accept inline edits, get explicit approval, then `gh issue create`. Start with sub-issues whose `Blocked by` is "None — can start immediately"; only publish a sub-issue after every sub-issue it lists as a blocker has been published.

Re-run the two-tier coverage check on the final approved list before the first sub-issue gets published.

---

## Issue title format

- `[feature] short title` or `[bug] short title`
- Bracketed prefix is **lowercase**
- Title cap is **70 characters total** (prefix included)
- **Sub-issues inherit the parent's prefix.** A feature parent's sub-issues are all `[feature] ...`; a bug parent's sub-issues are all `[bug] ...`
- **No `[parent]` marker.** Parent status lives in the body, not the title.

---

## AI disclaimer

Every published issue body — parent and sub — starts with the disclaimer block:

```
> *This was generated by AI during a new-issue grill session.*
```

This is enforced by the three body templates themselves (`template_feature_issue.md`, `template_bug_issue.md`, `template_subissue.md`), so as long as you start from the templates the disclaimer is already there. Do not strip it during inline edits.

---

## Handoff to `/implementation-planning`

After the final issue is published (whether one-plan or multi-plan), surface a short hint to the user:

> Next: run `/implementation-planning <issue-url>` to plan the HOW. Or just `/implementation-planning` — it can auto-detect the issue you just created in this session.

Then stop. Do not start a planning session yourself. The user invokes `/implementation-planning` when they are ready.

---

## Do not

A consolidated list of forbidden moves:

- Do **not** apply any GitHub label. Label vocabulary belongs to a future triage skill, not `new-issue`.
- Do **not** read source files during the grill. Vocabulary lookup in `CONTEXT.md`, `README.md`, and `docs/adr/` only.
- Do **not** modify `implementation-planning`'s standalone path.
- Do **not** publish any issue without an explicit preview-and-approve step from the user.
- Do **not** ask the user upfront whether the issue is one-plan or multi-plan. Claude evaluates and proposes after the full WHAT-grill, then confirms.
- Do **not** synthesise an issue from prior conversation context. Cold start or explicit one-liner seed only.
- Do **not** pull architecture, file paths, module names, or code snippets into any issue body. WHAT only.
- Do **not** include a `[parent]` marker in the parent title.
