# schoolwork

Study skills for a course folder. Installed with `install.sh` only, not part of the plugin.

| Skill | What it does |
|-------|--------------|
| `course-index` | Reads `Exams/` and `Exercises/` into `course-index.md`, with topic frequencies and the prerequisites for each question. |
| `lecture-preview` | Turns one slide deck into a one-page formula sheet to read before the lecture. |
| `lecture-notes` | Teaches a lecture one topic per session and writes the topic to `Lecture-notes/` once you can explain it and solve an exercise on it. |
| `write-formula-sheet` | Builds `formulas.md` and `formula-derivations.md` from the course material, grouped by use and ranked by exam frequency. |
| `example-workthrough` | Works one example end to end. Needs no course folder and writes nothing. |

The course folder the first four expect:

```
CourseRoot/
├── Lectures/           slide decks
├── Exercises/          optional
├── Exams/              optional
├── Lecture-notes/      output
├── course-index.md
├── formulas.md
└── formula-derivations.md
```
