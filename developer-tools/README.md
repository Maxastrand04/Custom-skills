# developer-tools

Coding skills that aren't stations on the kanban board. Reach for these whenever they're useful. There is no ordering, and no artifacts passed between them.

All of them are user-invoked, so each one starts only when I type its name.

| Skill | What it does |
|-------|--------------|
| `codebase-rules` | Grills a project's architecture and coding decisions into one-decision-per-file ADRs in `docs/adr/`. What `refactor-ticket` cites. |
| `challenge-adr` | The only door into an existing ADR. Tests whether a recorded decision still stands, and amends or retires it only on a case that beats it. No skill can open that door for me. |
| `add-comments` | Establishes a persisted `comment-convention.md`, then walks the code symbol by symbol with an approve/edit/skip preview. |
| `generate-framework-tests` | Real runnable tests (pytest / vitest / jest / go test / cargo test / JUnit), with fast-exit and drift-diff via a sidecar manifest. |
| `project-planning` | Once per project. Grills problem, user, success criteria, scope, and domain language, then writes `CONTEXT.md` and files one `(N) [epic]` skeleton issue per epic. Where the kanban board picks up. |
| `brainstorming` | The front door. Grills an idea trying to kill it; what survives gets a verdict and a route onto the board. |
| `pro-con` | Weigh a decision and commit to a recommendation. |
| `prune-skill` | Prunes a skill against a fixed list of smells: no-ops, duplication, sediment, sprawl, named models or users. Reports first, cuts after approval. |

The interview loop these lean on lives in `../behaviour/grilling`.
