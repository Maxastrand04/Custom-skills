# schoolwork

Study and comprehension skills, the ones for when I'm the learner, not the builder.

Two kinds of skill live here. `eli5` and `eli10` are levels I turn on for a session; the wording rules themselves live in `../behaviour/talk-to-middleschooler` and `../behaviour/talk-to-highschooler`, model-invoked so any other skill can reach for them. `lecture-notes` and `course-index` produce study material from a course folder.

`lecture-notes` has two kinds of run. The first invocation cuts the deck into topics and writes them as empty headings. Every invocation after that takes the next topic, teaches it, and fills its heading in. One topic per session, so context stays small and nothing gets written on a shrug.

The gate at the end of a topic is a real question off an exercise sheet, never an invented one. `course-index` records what each question needs you to know first, `lecture-notes` tracks which topics are covered across the whole `Lecture-notes/` folder, and a question becomes available the moment its last prerequisite lands. Questions that still need a later lecture wait, by name, until the topic that frees them is covered.

| Skill | Invocation | What it does |
|-------|------------|--------------|
| `eli5` | manual | Turns on middle-school mode for the rest of the session. Persistence and the off-switch only. |
| `eli10` | manual | Turns on high-school mode for the rest of the session. Persistence and the off-switch only. |
| `lecture-notes` | manual | Teaches one lecture topic by topic. A topic reaches `Lecture-notes/` only once I can explain it back and have worked a real question from `Exercises/`, written in whatever framing made it click. |
| `course-index` | manual | Reads `Exams/` and `Exercises/` once and writes `course-index.md`, including the topic frequency table and the per-question prerequisites `lecture-notes` reads. |

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

They connect by that file, not by invocation, the same way the `kanban/` chain does, where each step writes an artifact the next one reads. A course with no `Exams/` or `Exercises/` skips the high-yield flagging, and one with no `Exercises/` falls back to a transfer question at the gate.

Still planned: rehearsal, spaced repetition, exam prep.

`install.sh` already walks this directory, so a skill dropped in here with a valid `SKILL.md` installs with no changes to the installer.
