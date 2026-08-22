# behaviour

Skills that change how Claude talks rather than what it builds. No artifacts, no ordering. Each one is a wording or interaction rule that any other skill can borrow, which is why they sit at the root instead of inside `../developer-tools/` or `../schoolwork/`.

| Skill | Invocation | What it does |
|-------|------------|--------------|
| `grilling` | model | The bare interview loop. One question at a time, recommended answer first, down every branch until shared understanding. The primitive most of `../kanban/` is built on. |
| `unslop` | model | Cuts AI tells from any writing: puffery, em dashes, inline-header lists, filler, passive voice. Always applies. |
| `talk-to-middleschooler` | model | The wording rules for a reader who knows *nothing* about the subject. No naked terms, no equations, analogy for every invisible mechanism. |
| `talk-to-highschooler` | model | The wording rules for a reader with algebra and basic programming. Naked terms allowed once glossed; precision and notation kept. |

The two `talk-to-*` skills are the wording primitives behind `../schoolwork/eli5` and `../schoolwork/eli10`. Those own session persistence and the off-switch; the rules live here, once, reachable from any skill.

`install.sh` walks this directory, so a skill dropped in here with a valid `SKILL.md` installs with no changes to the installer.
