# schoolwork

Study and comprehension skills — the ones for when I'm the learner, not the builder.

Two kinds of skill live here. `eli5` and `eli10` are levels I turn on for a session; the wording rules themselves live in `../behaviour/talk-to-middleschooler` and `../behaviour/talk-to-highschooler`, model-invoked so any other skill can reach for them. `lecture-notes` and `course-index` produce study material from a course folder.

| Skill | Invocation | What it does |
|-------|------------|--------------|
| `eli5` | manual | Turns on middle-school mode for the rest of the session. Persistence and the off-switch only. |
| `eli10` | manual | Turns on high-school mode for the rest of the session. Persistence and the off-switch only. |
| `lecture-notes` | manual | One lecture's slide PDF becomes a revision file in `Lecture-notes/`. Fills what the deck leaves out and tags every filled line by source. |
| `course-index` | manual | Reads `Exams/` and `Exercises/` once and writes `course-index.md`, including the topic frequency table `lecture-notes` reads. |

A **naked term** is a domain word used before its gloss. Both wording primitives in `../behaviour/` ban shipping one; they differ in where the floor sits, meaning what counts as already known.

## The course folder

`lecture-notes` and `course-index` both work inside one course folder and never read outside it:

```
CourseRoot/
├── Lectures/           slide decks, the input
├── Exercises/          optional
├── Exams/              optional
├── Lecture-notes/      output
└── course-index.md     written by `course-index`, read by `lecture-notes`
```

They connect by that file, not by invocation — same as the `kanban/` chain, where each step writes an artifact the next one reads. A course with no `Exams/` or `Exercises/` just skips the high-yield flagging.

Still planned: rehearsal, spaced repetition, exam prep.

`install.sh` already walks this directory, so a skill dropped in here with a valid `SKILL.md` installs with no changes to the installer.
