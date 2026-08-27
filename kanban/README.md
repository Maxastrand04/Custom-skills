# kanban

The workflow skills. These run in order and each one writes an artifact the next one reads, so nothing is re-derived from memory:

```
project-planning  →  epic-planning  →  implementation-planning  →  implementation-plan-execute  →  review-diff
   CONTEXT.md         (N.M) tasks        implementation_plans/        code + green ACs           cleaned + committed
   project_plan.md    + epic issue       N.N_name.md
```

`new-ticket` sits beside the chain rather than on it. It files a standalone ticket for work no epic covers, and it owns
`new-ticket/ticket-shapes.md`, the single source of truth for every ticket body, title, label, and `gh` publish call.
`epic-planning` reads that same file, which is why an epic ticket and a standalone ticket look identical.

Otherwise a skill belongs here only if it's a link in that chain. Anything that helps while coding but isn't a station on the board lives in `../developer-tools/`.
