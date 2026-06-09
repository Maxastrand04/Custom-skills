Do not introduce structural choices (new modules, new patterns, new dependency directions, new cross-layer dependencies) not covered by `## Architecture decisions`. If a task requires one, stop and surface it to the user before writing code — never improvise structure. Cite the relevant `AD-N` when a task implements a decision.

{ACCEPTANCE_CRITERIA_BLOCK}

{ARCHITECTURE_DECISIONS_BLOCK}

This Group's tasks:
{GROUP_TASK_TABLE}
{GROUP_TESTS_CHECKS}

{PLAN_CLAUDE_INSTRUCTIONS}

Scoped exploration summary (only files this Group touches):
{SCOPED_EXPLORATION_SUMMARY}

Hard rule: Read only files named in your task table, file list, or exploration summary. Do NOT read CONTEXT.md, other plans, or unrelated source. If you hit a structural choice not covered by `## Architecture decisions`, stop and return:
  [ARCH GAP] <description> | Recommendation: <new AD wording or AD-N amendment>
Do NOT improvise structure.
