# Cutting a deck and writing the map

**A shared contract.** This file is published for any Skill that writes a lecture map, not just `lecture-notes`. `lecture-notes` greps the file this describes, so a map written loosely by anyone breaks every later run. Follow it as written.

## Cut the deck into topics

A topic is one idea worth one sitting. Most lectures hold 5 to 12. A slide range past a dozen slides is usually two topics wearing one heading, and a topic covering two slides is usually part of its neighbour.

Cut on where the idea changes, not where the section divider sits. Lecturers reuse one heading for a definition, its derivation, and three applications, and those are separate sittings.

Keep the deck's order. The notes get read alongside the slides, and later topics lean on earlier ones.

Then, if `course-index.md` exists at the course root, tie each topic to the index two ways.

**Name it.** Match the topic to the canonical topic names in the index and record which ones it covers. This is what makes exercises unlock later, since a topic the index does not recognise can never satisfy a question's prerequisite. One deck topic sometimes covers two canonical names, and sometimes none, which is fine and recorded as `none`.

**Count it.** Carry over its row in the frequency table, so the topic reads `**[high-yield]** 4 of 7 past exams`. That count sets how hard the topic gets pushed later, so a topic on five past papers does not get waved through on a shrug.

If `course-index.md` is missing, say so, recommend running `course-index` first, and carry on without either. Never read the exam PDFs directly and never copy an exam question into the notes.

**Done when:** every page of the deck falls inside exactly one topic's slide range, and every topic carries its canonical names and count, or the reason there are none.

## Write the map

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
