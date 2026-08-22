# schoolwork

Study and comprehension skills — the ones for when I'm the learner, not the builder.

Two levels, each a mode I turn on. The wording rules themselves live in `../behaviour/talk-to-middleschooler` and `../behaviour/talk-to-highschooler`, model-invoked so any other skill can reach for them when its output needs pitching at a learner.

| Skill | Invocation | What it does |
|-------|------------|--------------|
| `eli5` | manual | Turns on middle-school mode for the rest of the session. Persistence and the off-switch only. |
| `eli10` | manual | Turns on high-school mode for the rest of the session. Persistence and the off-switch only. |

A **naked term** is a domain word used before its gloss. Both wording primitives in `../behaviour/` ban shipping one; they differ in where the floor sits, meaning what counts as already known.

Still planned: note-taking, rehearsal, spaced repetition, exam prep.

`install.sh` already walks this directory, so a skill dropped in here with a valid `SKILL.md` installs with no changes to the installer.
