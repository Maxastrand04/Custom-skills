---
name: lecture-preview
description: Fly over a lecture deck before the lecture. Ranks every topic by how often it shows up on past papers, shows each one as a picture, table, or parallel rather than prose, and says what to listen for.
disable-model-invocation: true
---

# lecture-preview

A **flyover** of a deck, read before the lecture. You cross the whole terrain, see the shape of every topic, and land on none of them. Landing is what `lecture-notes` does afterwards.

Afterwards the user can name every topic, say what each one is for, say which ones the exam keeps asking about, and know what to have their ear open for when the lecturer gets there. They still cannot do any of it. That gap is the point. Walking in with a map and three specific open questions beats walking in with a half-learned version of the lecture about to be delivered.

**The budget is 15 to 30 minutes of the user's reading time.** Every rule here exists to hold it, and the whole thing fails if it becomes a second lecture.

Invoke `unslop` for everything written to the file.

## Step 1: Locate the course and settle the run

The deck's folder is normally `Lectures/`, and the course root is that folder's parent. Only these siblings matter:

```
CourseRoot/
├── Lectures/           the deck
├── Exercises/          optional
├── Exams/              optional
├── Lecture-notes/      output, both files land here, created if missing
└── course-index.md     optional, written by the `course-index` skill
```

Never read above the course root or outside it.

Two files come out of this run, both under `Lecture-notes/`:

- `<deck-filename>.md`, the topic map, shared with `lecture-notes`. **Written only if missing. Never overwritten.** If it already exists, its headings are the topic cut for this run, and step 3 is skipped entirely.
- `<deck-filename>-preview.md`, the flyover. Rewritten whole on every run, since it is disposable by design.

This is the one place to ask questions. Ask if the deck is ambiguous, if the course root does not resolve, or if the user knows something about the lecture that changes what matters. One round, and only here. Once writing starts, the run is one-shot.

**Done when:** the course root is resolved, both output paths are fixed, the map is recorded as present or missing, and `course-index.md` is recorded as present or missing.

## Step 2: Read every page of the deck

The Read tool caps a PDF at 20 pages per call and needs an explicit `pages` range past 10. Get the page count first, then read consecutive batches until the last page is covered.

A flyover that skipped the last third of the deck is worse than none, because the user trusts it and walks in blind to exactly the part they did not know was coming.

**Done when:** the highest page read equals the deck's total page count. Every page.

## Step 3: Cut the deck into topics and write the map

Skip this step when the map already exists.

Cut the deck and write the map file by [`../lecture-notes/map-format.md`](../lecture-notes/map-format.md). Follow it as written, including how topics are matched to the canonical names in `course-index.md`, how the frequency counts are carried over, and the exact ` · ` separators in each metadata line. `lecture-notes` greps that file, so a map written loosely here breaks it later.

Two changes for this skill. The header's video field reads `Video: not asked`, since the lecture has not happened yet and there is nothing to fetch. And every metadata line still ends `Not covered yet.`, because a flyover covers nothing.

**Done when:** `Lecture-notes/<deck-filename>.md` exists, its headings cover every page of the deck in order, its header reads `Video: not asked`, and every metadata line ends `Not covered yet.`

## Step 4: Rank the topics

The ranking is the most useful thing in the document. An hour of lecture is not uniformly worth attention, and knowing which twenty minutes to concentrate in is most of what a preview buys.

Read the frequency table in `course-index.md` and give every topic one of three calls:

| Call | When | What it buys the topic |
|---|---|---|
| `read closely` | top of the frequency table, or on most past papers | the fullest treatment, up to 150 words |
| `know it exists` | on a paper or two | about 80 words |
| `skim` | on no paper, or setup for a later topic | one or two sentences, and no visual |

Rank against this course's own table, not against a general sense of what matters in the subject. A topic on five of seven papers is `read closely` even when it looks like an aside on the slides, and that mismatch is worth saying out loud in the document.

With no `course-index.md`, say so in the report, recommend running `course-index` first, and rank by how much of the deck each topic takes up instead. Say in the document that the ranking is by slide count and not by exams, so nobody revises off it. Never read the exam PDFs directly to patch the gap. That is what makes `course-index` cheap and repeatable.

**Done when:** every topic carries one of the three calls, and the basis for the ranking is recorded as exam frequency or slide count.

## Step 5: Cut out the slides worth recognising

The lecturer's own figure is the best visual available, and it is better than anything drawn from scratch, because seeing it again on the projector is what makes the preview pay off in the room.

Render whole slide pages at 150 dpi:

```bash
mkdir -p "Lecture-notes/.assets"
pdftoppm -png -r 150 -f <page> -l <page> "Lectures/<deck>.pdf" "Lecture-notes/.assets/<deck-stem>-p<page>"
```

Pick one slide per topic at most, and only where the slide carries a diagram, a plot, a worked shape, or a picture. A slide of bullet points is not worth an image and the deck is already open next to the user. `read closely` topics get first claim. Skip images entirely on `skim` topics.

**Done when:** every rendered file exists on disk under `Lecture-notes/.assets/`, and no topic has more than one.

## Step 6: Write the flyover

Rewrite `Lecture-notes/<deck-filename>-preview.md` whole:

```markdown
# Flyover: <Lecture title>

> Deck: `Lectures/<file>.pdf` · Written: <YYYY-MM-DD> · Ranked by: past papers
> A flyover, not notes. Nothing here is worked out, and nothing here is in your words yet.
> Run `lecture-notes` on this deck after the lecture.

## What this lecture is doing

<Two or three sentences. The problem the lecture is solving, and where it ends up.
Not a list of the topics, that is the next table.>

## Where to spend your attention

| # | Topic | Slides | Past papers | Call |
|---|---|---|---|---|
| 1 | Matrix multiplication | 4-11 | 2 of 7 | know it exists |
| 2 | Eigenvectors | 12-20 | 5 of 7 | read closely |

## 2. Eigenvectors (slides 12-20) · 5 of 7 past papers · read closely

<One paragraph in plain words. What it is and what it is for. No derivation.>

![slide 14](.assets/lec3-p14.png)

**Like** a spinning globe, where every point moves except the two on the axis. Those two
are the eigenvectors. The parallel breaks as soon as the map stretches rather than
rotates, and most of them do.

**Where this goes.** Slide 21 onwards uses it for diagonalization, so a shaky grip here
costs you the rest of the lecture.

**Listen for** why the eigenvalue can be negative. The slides state it and never say what
it means.
```

Rules for the body:

- **One visual per topic, never two.** A second visual on one topic is the flyover losing altitude. Pick by what the topic is: a figure the lecturer drew becomes an extracted slide, a set of things told apart by a few properties becomes a table with one row each, a process or a dependency becomes a mermaid flowchart, and a shape or a growth rate becomes a few lines of ASCII. Mermaid renders in Obsidian, VS Code, and GitHub, so keep the blocks small enough to read as source anyway.
- **One parallel per topic, bounded in the same breath.** Say where it breaks in the sentence that makes it. An analogy nobody has bounded gets over-trusted, and an over-trusted one sends the user into the lecture confidently wrong, which is worse than blank.
- **Where this goes** names the later topic or the later course that leans on this one. Where nothing does, drop the line.
- **Listen for** is one question or one thing to catch, aimed at what the slides state without explaining. Generic attention advice is not a listen-for. If the slides genuinely cover it, drop the line rather than inventing a gap.
- **No derivations, no proofs, no worked examples, no exercises.** The moment a topic gets worked through, the reading time doubles and `lecture-notes` has nothing left to do. State what a method produces and move on.
- A formula appears only when the formula is the topic itself. Then it goes in a `$$` block alone on its own lines with its symbols named in words underneath. **No inline math anywhere.** No `$x$`, no `\( \)`, no LaTeX in backticks. Bare Latin letters are written bare, Greek letters are spelled out as words. The full rule and its rewrite table are in [`../lecture-notes/teaching.md`](../lecture-notes/teaching.md).
- No slide-bullet recopying. A section that reads like the slide it came from has bought the user nothing they would not get from opening the deck.

Then check both hard limits:

```bash
wc -w "Lecture-notes/<deck-filename>-preview.md"
grep -n '\$' "Lecture-notes/<deck-filename>-preview.md" | grep -v ':\$\$$'
```

Under 1200 words means topics got skipped. Over 2600 means it stopped being a flyover, and the fix is cutting the `read closely` sections, not trimming adverbs everywhere. Every line the grep prints is inline math that slipped through; rewrite it and run it again.

**Done when:** every topic in the map has a section in deck order, each carries at most one visual, the word count is between 1200 and 2600, and the grep returns nothing.

## Step 7: Report

Say where the flyover is, how many topics it covers, which ones are `read closely` and why, and whether the map was written fresh or already existed. If `course-index.md` was missing, say the ranking is by slide count and recommend running `course-index`. Then stop. No teaching in this session.
