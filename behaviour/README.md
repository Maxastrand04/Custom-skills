# behaviour

Skills that change how Claude talks rather than what it builds. No ordering, and no artifacts in the repo. Each one is a wording or interaction rule that any other skill can borrow, which is why they sit at the root instead of inside `../developer-tools/` or `../schoolwork/`.

| Skill | Invocation | What it does |
|-------|------------|--------------|
| `grilling` | model | The bare interview loop. Maps the plan as a design tree, asks the whole frontier of resolvable questions per round with a recommended answer for each, and dispatches sub-agents for anything answerable from the codebase instead of asking. The primitive most of `../kanban/` is built on. |
| `unslop` | model | Cuts AI tells from any writing: puffery, em dashes, inline-header lists, filler, passive voice. Always applies. |
| `gloss-me` | model | Decides which terms get glossed. Checks each domain term against my glossary of known terms at `~/.claude/glossary.md`, glosses the rest in a short block before the paragraph that first uses them, and ends each response with one footer asking which new terms I'm comfortable with. A term I don't get starts a loop of synonyms, re-glosses, or rewrites, then picks up where it left off. The only skill that writes the glossary. `/gloss-me` with nothing in progress seeds it one domain at a time. |
| `talk-to-middleschooler` | model | The wording rules for a reader who knows *nothing* about the subject. `gloss-me` with the floor lowered to nothing, no equations, analogy for every invisible mechanism. |
| `talk-to-highschooler` | model | The wording rules for a reader with algebra and basic programming. `gloss-me` at its default floor; precision and notation kept. |
| `science-output` | model | The format rules for anything with math in it. Every expression in a `$$` block, symbols named underneath, at most three sentences that say why the step happened rather than restating it. |

The two `talk-to-*` skills are the wording primitives behind `../schoolwork/eli5` and `../schoolwork/eli10`. Those own session persistence and the off-switch; the rules live here, once, reachable from any skill.

`science-output` is the same arrangement for math. The inline-math ban and its rewrite table used to live inside `../schoolwork/lecture-notes/teaching.md`, which is a strange home for a rule three skills reach for, so they moved here. `lecture-notes`, `lecture-preview`, and `example-workthrough` all invoke it and hold no math rules of their own.

One thing it does that the `talk-to-*` pair does not: it restricts the LaTeX to what stays legible as raw source, since most of this output is read in a terminal where nothing renders. That costs the notes files nothing, because `\underbrace` was never making them better.

`gloss-me` is the one skill here with state. The glossary lives in `~/.claude/`, not this repo, because what I know follows me across projects. Project vocabulary I've confirmed goes under a per-project heading in the same file and only counts inside that project. A project's `CONTEXT.md` never counts, since it records what the project means, not what I know. `grilling`, both `talk-to-*` skills, `pro-con`, `refactor-ticket` and `unit-test-ticket` borrow it, so every skill that talks to me glosses the same way from one list.

`install.sh` walks this directory, so a skill dropped in here with a valid `SKILL.md` installs with no changes to the installer.
