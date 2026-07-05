Do not introduce structural choices (new modules, new patterns, new dependency directions, new cross-layer dependencies) not covered by `## Architecture decisions`. If a task requires one, stop and surface it to the user before writing code — never improvise structure. Cite the relevant `AD-N` when a task implements a decision.

Plan file: {PLAN_FILE_PATH}
Your Group: {GROUP_LABEL}

Read {PLAN_FILE_PATH} yourself and load only these sections — do not read the rest of the plan:
- `## Acceptance criteria`
- `## Architecture decisions` (including the mock code snippet)
- The `### {GROUP_LABEL}` block: its task table, file list, and `Tests / checks` sub-block
- `## Claude Instructions`

Exploration summary: read {EXPLORATION_SUMMARY_PATH}, scoped to the files named in your Group's file list. Do not read entries for other Groups.

Hard rule: read only the plan sections and exploration-summary entries listed above, plus the files named in your task table. Do NOT read CONTEXT.md, other plans, or unrelated source.

If you hit a structural choice not covered by `## Architecture decisions`, stop and return:
  [ARCH GAP] <description> | Recommendation: <new AD wording or AD-N amendment>
Do NOT improvise structure.
