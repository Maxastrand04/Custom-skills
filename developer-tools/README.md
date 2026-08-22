# developer-tools

Coding skills that aren't stations on the kanban board. Reach for these whenever they're useful — no ordering, no artifacts passed between them.

| Skill | What it does |
|-------|--------------|
| `codebase-rules` | Grills a project's architecture and coding rules into one-rule-per-file ADRs in `docs/adr/`. What `review-diff` cites. |
| `add-comments` | Establishes a persisted `comment-convention.md`, then walks the code symbol by symbol with an approve/edit/skip preview. |
| `generate-framework-tests` | Real runnable tests (pytest / vitest / jest / go test / cargo test / JUnit), with fast-exit and drift-diff via a sidecar manifest. |
| `implement-tdd` | The small-change bypass around the board: red tests, one implementer per attempt, reviewer on green. |
| `new-issue` | WHAT grill → GitHub Issue, for work no epic covers. Splits oversized scope into linked sub-issues. |
| `brainstorming` | The front door. Grills an idea trying to kill it; what survives gets a verdict and a route onto the board. |
| `pro-con` | Weigh a decision and commit to a recommendation. Manual invocation only. |

The interview loop these lean on lives in `../behaviour/grilling`.
