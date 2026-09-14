# schoolwork

Study and comprehension skills, the ones for when I'm the learner, not the builder.

Two kinds of skill live here. `eli5` and `eli10` set the level of an explanation; the wording rules themselves live in `../behaviour/talk-to-middleschooler` and `../behaviour/talk-to-highschooler`, model-invoked so any other skill can reach for them. Neither `eli*` skill persists. They used to claim they held for the rest of the session, and that never worked, so now they don't claim it. Type the name again when you want the level again.

`lecture-preview`, `lecture-notes`, `course-index`, and `write-formula-sheet` produce study material from a course folder.

`example-workthrough` stands apart from the rest. It is manual, like every other skill in this folder, and the only one that needs no course folder. It lays out the principle and the formulas it will use, asks which of them are new to you, then works the example to a result. `lecture-preview` used to carry its own copy of that and now points at it instead.

`lecture-preview` runs before the lecture and `lecture-notes` runs after it. The preview is a formula sheet for one deck: every formula that deck introduces, its symbols named, one line on when you reach for it, and three sentences on what the lecture is doing. You scan it while working exercises rather than reading it. If any formula on the sheet is unclear, use `example-workthrough` to get it described well.

`lecture-notes` has two kinds of run. The first invocation cuts the deck into topics and writes them as empty headings. Every invocation after that takes the next topic, teaches it, and fills its heading in. One topic per session, so context stays small and nothing gets written on a shrug.

The gate at the end of a topic is a real question off an exercise sheet, never an invented one. `course-index` records what each question needs you to know first, `lecture-notes` tracks which topics are covered across the whole `Lecture-notes/` folder, and a question becomes available the moment its last prerequisite lands. Questions that still need a later lecture wait, by name, until the topic that frees them is covered.

| Skill | Invocation | What it does |
|-------|------------|--------------|
| `eli5` | manual | Explains at middle-school level. Points at the wording rules, nothing else. |
| `eli10` | manual | Explains at high-school level. Points at the wording rules, nothing else. |
| `lecture-preview` | manual | Turns one deck into a one-page formula sheet before the lecture. Every formula the deck introduces, its symbols named, one line on when to reach for it. Works an example on demand. |
| `lecture-notes` | manual | Teaches one lecture topic by topic. A topic reaches `Lecture-notes/` only once I can explain it back and have worked a real question from `Exercises/`, written in whatever framing made it click. |
| `course-index` | manual | Reads `Exams/` and `Exercises/` once and writes `course-index.md`, including the topic frequency table and the per-question prerequisites `lecture-notes` reads. |
| `example-workthrough` | manual | Works one example end to end, opening with the theory and the formulas it will use. Answers in chat, writes nothing. |
| `write-formula-sheet` | manual | Builds the cheat sheet. Reads the lectures, exercises, and exams for every formula they state, groups them by what you use together, ranks the groups by exam frequency, and writes `formulas.md` with `formula-derivations.md` beside it. |

A **naked term** is a domain word used before its gloss. Both wording primitives in `../behaviour/` ban shipping one; they differ in where the floor sits, meaning what counts as already known.

## The course folder

All four work inside one course folder and never read outside it:

```
CourseRoot/
├── Lectures/           slide decks, the input
├── Exercises/          optional
├── Exams/              optional
├── Lecture-notes/      output, both the notes and the formula sheet
├── course-index.md     written by `course-index`, read by the other three
├── formulas.md         written by `write-formula-sheet`
└── formula-derivations.md
```

They connect by that file, not by invocation, the same way the `kanban/` chain does, where each step writes an artifact the next one reads. A course with no `Exams/` or `Exercises/` skips the high-yield flagging, and one with no `Exercises/` falls back to a transfer question at the gate.

`write-formula-sheet` is the odd one out on state. It keeps no manifest, so the sheet it wrote last time is the only record of what it has already seen, which is why every entry carries the slide it came from. A re-run reads the material again, regroups the whole sheet around whatever is new, and never appends to the bottom. Formulas whose topic the exams never touch drop to a one-line list at the foot of the file, kept only so the next run does not find them and add them all over again.

Still planned: rehearsal, spaced repetition, exam prep.

`install.sh` already walks this directory, so a skill dropped in here with a valid `SKILL.md` installs with no changes to the installer.
