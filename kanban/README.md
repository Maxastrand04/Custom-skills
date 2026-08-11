# kanban

The workflow skills. These run in order and each one writes an artifact the next one reads, so nothing is re-derived from memory:

```
project-planning  →  sprint-planning  →  implementation-planning  →  implementation-plan-execute  →  review-edits
   CONTEXT.md          (N.M) tasks         implementation_plans/        code + green ACs               verdict
   project_plan.md     + sprint issue      N.N_name.md
```

A skill belongs here only if it's a link in that chain. Anything that helps while coding but isn't a station on the board lives in `../developer-tools/`.
