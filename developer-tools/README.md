# developer-tools

Coding skills that aren't stations on the kanban board. Reach for these whenever they're useful. There is no ordering, and no artifacts passed between them.

All of them are user-invoked, so each one starts only when I type its name.

| Skill | What it does |
|-------|--------------|
| `challenge-pcr` | The only door into an existing PCR, the project-wide conventions in `docs/pcr/`. Tests whether a convention still stands, and amends or retires it only on a case that beats it. No skill can open that door for me. |
| `generate-framework-tests` | Real runnable tests (pytest / vitest / jest / go test / cargo test / JUnit), with fast-exit and drift-diff via a sidecar manifest. |
| `project-planning` | Once per project. Grills problem, user, success criteria, scope, domain language, and project conventions, then writes `CONTEXT.md`, seeds `docs/pcr/`, and files one `(N) [epic]` skeleton issue per epic. Where the kanban board picks up. |
| `brainstorming` | The front door. Grills an idea trying to kill it; what survives gets a verdict and a route onto the board. |
| `pro-con` | Weigh a decision and commit to a recommendation. |
| `prune-skill` | Prunes a skill against a fixed list of smells: no-ops, duplication, sediment, sprawl, named models or users. Reports first, cuts after approval. |

The interview loop these lean on lives in `../behaviour/grilling`.
