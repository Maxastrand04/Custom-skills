---
name: lecture-notes
description: Turn one lecture's slide PDF into a revision file in Lecture-notes/, filling what the slides leave out and tagging where every filled line came from.
disable-model-invocation: true
---

# lecture-notes

Turn one lecture's slide deck into a markdown revision file.

Slides are fragments. A formula with no derivation, a diagram with no caption, three words that stood for five minutes of talking. Notes worth revising from have to carry what the deck only gestures at, which means pulling from outside it. Everything pulled from outside the deck is tagged, so the reader can always separate the lecturer's claim from a model's guess.

Invoke `talk-to-highschooler` for the wording of the notes file. Invoke `unslop` for its prose. Neither is restated here.

## Provenance

Three sources, three tags. The legend goes at the top of every notes file.

| Source | Tag | Meaning |
|---|---|---|
| The deck | none | On the slides. The default, untagged. |
| The video | `[🎙 12:34]` | Said out loud, not on the slides. The timestamp jumps back to it. |
| Claude | `[fill]` | In neither. Unverified, check before trusting it in an exam. |

Tag the sentence, not the section. A paragraph mixing deck content and filled content gets its filled sentences tagged one by one.

This holds the file's one guarantee: `grep '\[fill\]' <file>` lists everything invented. Untagged filled text breaks it.

## Step 1 — Locate the course

The deck's own folder is normally `Lectures/`, and the course root is that folder's parent. Only these siblings of the course root matter:

```
CourseRoot/
├── Lectures/           the deck
├── Exercises/          optional
├── Exams/              optional
├── Lecture-notes/      output, created if missing
└── course-index.md     optional, written by the `course-index` skill
```

Never read above the course root or outside it. A course with no `Exercises/` or `Exams/` is normal, not an error, and not a reason to go looking elsewhere.

**Done when:** the course root is resolved, the output path is fixed at `Lecture-notes/<deck-filename>.md`, and each of the four siblings is recorded present or absent.

## Step 2 — Settle the video

A YouTube link passed with the invocation is the lecture video; use it. If no link was passed, ask once whether one exists. A "no" fixes the deck-only path for the rest of the run, so do not ask again.

With a link, read `transcript.md` in this skill directory and follow it.

**Done when:** either a timestamped transcript exists on disk, or this run is recorded as having no video.

## Step 3 — Read every page of the deck

The Read tool caps a PDF at 20 pages per call and requires an explicit `pages` range past 10. Get the deck's page count first, then read consecutive batches until the last page is covered.

**Done when:** the highest page read equals the deck's total page count. Not "the substance is covered" and not "the rest is summary slides". Every page.

## Step 4 — Flag the high-yield topics

Skip this step entirely when both `Exercises/` and `Exams/` are absent.

Read `course-index.md` at the course root and use its frequency table to flag topics in this deck that keep recurring:

```
**[high-yield]** appeared in 4 of 7 past exams
```

If `course-index.md` is missing but `Exams/` or `Exercises/` exists, say so and recommend running `course-index` first, then carry on without the flags. Do not read the exam PDFs directly. Reading them once, into an index, is the whole reason that skill exists.

Flag the topic and its count. Never copy an exam question into the notes.

**Done when:** every topic section in the deck has been checked against the index's frequency table, or the step was skipped for one of the two reasons above.

## Step 5 — Write the file

Follow the deck's own order so the notes can be read alongside the slides. Anchor each section to its slide numbers.

```markdown
# <Lecture title>

> Deck: `Lectures/<file>.pdf` · Video: <yes / no> · Written: <YYYY-MM-DD>
> `[🎙 mm:ss]` said in the video · `[fill]` added by Claude, unverified · `**[high-yield]**` recurs in past exams

## In one paragraph
What this lecture is about and why it comes where it does in the course.

## 1. <Topic> (slides 4-11)
Connected prose, not recopied bullets. A slide that reads "SGD: noisy, cheap, escapes minima"
becomes sentences that say what stochastic gradient descent is, why sampling one batch at a
time makes it noisy, and how that noise is what lets it climb out of a bad valley. [fill]

**Formula.** Every symbol named in words, right under it.

## 2. <Topic> (slides 12-20)
...

## Terms
| Term | What it means |
|---|---|
| ... | ... |

## Open questions
Things the deck raises and never answers, and anything left uncertain. Say what is unclear
rather than filling it and tagging it.
```

Rules for the body:

- No naked terms. Any domain word gets its plain-words gloss in the sentence it first appears in, and again in the Terms table. `talk-to-highschooler` owns where the floor sits.
- Prose over bullets. A bullet list that mirrors the slide's bullet list has added nothing.
- Every formula gets its symbols named. An unexplained formula is a picture.
- A diagram or plot the deck shows gets described in words, since the notes file has no image.
- Uncertainty goes to Open questions, not into a `[fill]`. Tag what is filled and confident; list what is unresolved.

**Done when:** the file is written, every section maps to a slide range, and every non-deck sentence carries its tag.

## Step 6 — Report

State four things and stop: the output path, whether the video branch ran, the number of `[fill]` tags, and the number of `[high-yield]` flags. Point at the grep line so the fills can be audited in one command.
