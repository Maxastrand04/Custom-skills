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
- **Present, header reads `Video: not asked`** -> `lecture-preview` wrote the map before the lecture and never settled the video. Do step 2 only, rewrite the header field with what it returns, then carry on into `teaching.md`.
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

**Done when:** either a timestamped transcript sits at `Lecture-notes/.transcripts/<deck-filename>.srt`, or the map's header line records `Video: no`.

## Step 3: Read every page of the deck

The Read tool caps a PDF at 20 pages per call and requires an explicit `pages` range past 10. Get the deck's page count first, then read consecutive batches until the last page is covered.

**Done when:** the highest page read equals the deck's total page count. Not "the substance is covered" and not "the rest is summary slides". Every page.

## Step 4: Cut the deck into topics and write the map

Both are defined in [`map-format.md`](map-format.md), which `lecture-preview` reads too. Follow it as written, since every later run greps the file it describes.

**Done when:** its two "Done when" lines both hold, meaning every deck page falls inside exactly one topic's slide range, and the map exists with every metadata line ending `Not covered yet.`

## Step 5: Report

Say where the file is, how many topics there are, whether a transcript landed, and which topics are high-yield. If `course-index.md` was missing, say that exercises cannot be unlocked until it exists. Then tell the user to invoke the skill again to start topic 1. Do not start teaching in this session.
