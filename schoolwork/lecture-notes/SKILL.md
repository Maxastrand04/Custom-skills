---
name: lecture-notes
description: Work through a lecture one topic at a time, teaching each until it clicks, and write a topic into Lecture-notes/ only once the user can explain it back and has worked a real exercise it unlocks.
disable-model-invocation: true
---

# lecture-notes

Teach one lecture topic by topic. The notes file is what the understanding leaves behind, not the goal of the run.

A generated summary of a deck is a document nobody learned anything from. So nothing gets written until the user has explained the topic back in their own words and worked a real question from the course's own `Exercises/`. What lands on the page is the path that got them there, in the language that got them there, so re-reading it six weeks later replays the click instead of re-teaching from scratch.

One topic per session. Context stays small and each topic gets the whole window.

## Which run is this

Check for `Lecture-notes/<deck-filename>.md`.

- **Missing** -> this is the map run. Steps 1 to 5 below, then stop. No teaching.
- **Present** -> this is a topic run. Read [`teaching.md`](teaching.md) and follow it. Nothing else on this page applies.

## Step 1: Locate the course

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

## Step 2: Settle the video

The video is a teaching source. Every later topic run reads the span of transcript covering its slides, so fetching it once here is what makes it available at all.

A YouTube link passed with the invocation is the lecture video; use it. If no link was passed, ask once whether one exists. A "no" fixes the deck-only path for the whole lecture, so do not ask again on later runs.

With a link, read [`transcript.md`](transcript.md) and follow it.

**Done when:** either a timestamped transcript sits at `Lecture-notes/.transcripts/<deck-filename>.srt`, or the header line written in step 5 records `Video: no`.

## Step 3: Read every page of the deck

The Read tool caps a PDF at 20 pages per call and requires an explicit `pages` range past 10. Get the deck's page count first, then read consecutive batches until the last page is covered.

**Done when:** the highest page read equals the deck's total page count. Not "the substance is covered" and not "the rest is summary slides". Every page.

## Step 4: Cut the deck into topics

A topic is one idea worth one sitting. Most lectures hold 5 to 12. A slide range past a dozen slides is usually two topics wearing one heading, and a topic covering two slides is usually part of its neighbour.

Cut on where the idea changes, not where the section divider sits. Lecturers reuse one heading for a definition, its derivation, and three applications, and those are separate sittings.

Keep the deck's order. The notes get read alongside the slides, and later topics lean on earlier ones.

Then, if `course-index.md` exists at the course root, tie each topic to the index two ways.

**Name it.** Match the topic to the canonical topic names in the index and record which ones it covers. This is what makes exercises unlock later, since a topic the index does not recognise can never satisfy a question's prerequisite. One deck topic sometimes covers two canonical names, and sometimes none, which is fine and recorded as `none`.

**Count it.** Carry over its row in the frequency table, so the topic reads `**[high-yield]** 4 of 7 past exams`. That count sets how hard the topic gets pushed later, so a topic on five past papers does not get waved through on a shrug.

If `course-index.md` is missing, say so, recommend running `course-index` first, and carry on without either. Never read the exam PDFs directly and never copy an exam question into the notes.

**Done when:** every page of the deck falls inside exactly one topic's slide range, and every topic carries its canonical names and count, or the reason there are none.

## Step 5: Write the map

Write the file as headings with empty bodies. The queue and the notes are the same document, so there is one place to look and one place to update.

```markdown
# <Lecture title>

> Deck: `Lectures/<file>.pdf` · Video: <yes / no> · Started: <YYYY-MM-DD>
> `[🎙 12:34]` marks something said in the video and not on the slides. Everything untagged is how I explained it back.
> Progress: 0 of 9 topics.

## 1. <Topic> (slides 4-11)
> Indexed as: Matrix multiplication · Not covered yet.

## 2. <Topic> (slides 12-20)
> Indexed as: Eigenvalues and eigenvectors · **[high-yield]** 4 of 7 past exams · Not covered yet.
```

That one metadata line per topic carries everything the later runs need. A topic run finds its next topic by scanning for the first line still ending `Not covered yet.`, and works out which exercises are unlocked by reading the `Indexed as` names off every line in `Lecture-notes/` already marked `Covered`. Both greps are exact, so keep the field names and the ` · ` separators as written.

Nothing else goes in. No summary of the lecture, no orientation paragraph, since every word of the body is the user's own and none of it is written yet. Headings carry no notation either. Name things in words, the way [`teaching.md`](teaching.md) requires of every later run.

**Done when:** the file exists, the headings cover the deck in order, every metadata line ends `Not covered yet.`, and the progress line says 0.

## Step 6: Report

Say where the file is, how many topics there are, whether a transcript landed, and which topics are high-yield. If `course-index.md` was missing, say that exercises cannot be unlocked until it exists. Then tell the user to invoke the skill again to start topic 1. Do not start teaching in this session.
