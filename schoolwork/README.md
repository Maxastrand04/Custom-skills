# schoolwork

Study and comprehension skills — the ones for when I'm the learner, not the builder.

Two levels, each split into a mode I turn on and a primitive that owns the wording rules. The `talk-to-*` pair are model-invoked, so any other skill can reach for them when its output needs pitching at a learner.

| Skill | Invocation | What it does |
|-------|------------|--------------|
| `eli5` | manual | Turns on middle-school mode for the rest of the session. Persistence and the off-switch only. |
| `eli10` | manual | Turns on high-school mode for the rest of the session. Persistence and the off-switch only. |
| `talk-to-middleschooler` | model | The wording rules for a reader who knows *nothing* about the subject. No naked terms, no equations, analogy for every invisible mechanism. |
| `talk-to-highschooler` | model | The wording rules for a reader with algebra and basic programming. Naked terms allowed once glossed; precision and notation kept. |

A **naked term** is a domain word used before its gloss. Both primitives ban shipping one; they differ in where the floor sits — what counts as already known.

Still planned: note-taking, rehearsal, spaced repetition, exam prep.

`install.sh` already walks this directory, so a skill dropped in here with a valid `SKILL.md` installs with no changes to the installer.
