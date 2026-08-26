---
name: course-index
description: Read every PDF in a course's Exams/ and Exercises/ folders once and write course-index.md, covering what each file holds, plus the topic frequency table that lecture-notes reads to flag high-yield material.
disable-model-invocation: true
---

# course-index

Read a course's past exams and exercise sheets once, and write down what is in them.

Without this, every `lecture-notes` run would re-read the whole exam back-catalogue to work out what matters. Twenty old exams is unaffordable per lecture and gives a different answer each time, depending on what fit in context that day. Indexing once makes the signal cheap and makes it the same on every run.

Invoke `unslop` for the prose of the index file.

## The contract

`course-index.md` is read by `lecture-notes`, which consumes exactly one thing: the frequency table. Its shape is fixed. Change it and the other skill goes blind.

The index records what each file covers and how often each topic recurs. It never becomes a solutions document, because the point is knowing what to study, not having the answers to last year's questions.

## Step 1: Locate and scope

The course root holds `Lectures/`, and may hold `Exercises/` and `Exams/`. Run from the course root, or resolve it from wherever the user pointed.

Index PDFs directly inside `Exams/` and `Exercises/`, plus one level of subfolder beneath them (courses often file exams by year). Nothing else in the course, and nothing above the course root.

Stop and say so when neither folder exists. There is nothing to index.

**Done when:** the course root is resolved and the full list of PDFs to consider is enumerated, each labelled exam or exercise.

## Step 2: Fast-exit

The manifest at `<CourseRoot>/.course-index/manifest.json` records every file already indexed:

```json
{
  "files": {
    "Exams/2024-01-12.pdf": { "sha256": "…", "indexed_at": "2026-08-24", "topics": ["…"] }
  },
  "topics": ["…canonical topic names, in first-seen order…"]
}
```

Hash each PDF with `shasum -a 256`. A file whose hash matches its manifest entry is done; skip it.

When every PDF matches and no new ones appeared, print `course-index is up to date, nothing to do` and exit. No reads, no writes, no plan.

**Done when:** every enumerated PDF is sorted into unchanged (skip) or new-or-changed (index).

## Step 3: Read the new files

For each file to index, read it in 20-page batches to the last page, the same cap `lecture-notes` works under.

Pull out, per file:

- What it is: exam or exercise sheet, and its date or number if the filename or first page says
- The topics it tests, one line each, saying what the student actually has to do with the topic
- Roughly how much of the paper each topic takes up

Do not transcribe questions and do not solve them.

**Done when:** every new-or-changed file has been read to its last page and has a topic list.

## Step 4: Normalize the topics

This step is what makes the frequency table worth anything. One lecturer writes "gradient descent", the next year's paper says "GD", a third says "steepest descent". Left alone, one topic appearing in three exams looks like three topics appearing once, and nothing is ever flagged high-yield.

So: match every extracted topic against the manifest's canonical `topics` list first. Reuse the existing name whenever the underlying topic is the same, even when the wording differs. Only mint a new canonical name when nothing on the list covers it.

Pitch the names at the level a lecture covers. "Eigenvalues" is a topic. "Linear algebra" is a course, and "computing eigenvalues of a 3x3 matrix by hand" is a question. Both extremes make the table useless, one by flagging everything and the other by flagging nothing.

**Done when:** every topic on every file's list is either an existing canonical name or a deliberately added new one, and no two canonical names mean the same thing.

## Step 5: Write the index

Write `<CourseRoot>/course-index.md`, rebuilt whole from the manifest so unchanged files keep their entries:

```markdown
# Course index

> Indexed: <YYYY-MM-DD> · <N> exams · <M> exercise sheets
> Written by the `course-index` skill. Re-run it after adding files.

## Topic frequency

| Topic | Exams | Exercises | Total |
|---|---|---|---|
| Eigenvalues and eigenvectors | 5 | 3 | 8 |
| Singular value decomposition | 2 | 1 | 3 |

## Exams

### Exams/2024-01-12.pdf
Covers: eigenvalues and eigenvectors (about half the paper), singular value
decomposition, matrix norms.

## Exercises

### Exercises/sheet-03.pdf
Covers: eigenvalues and eigenvectors, diagonalization.
```

Sort the frequency table by Total, descending. That ordering is part of the contract.

Then write the manifest, with every indexed file's hash and the canonical topic list.

**Done when:** `course-index.md` and the manifest are both written, the table's counts agree with the per-file entries, and every file in the manifest appears in the index.

## Step 6: Report

State how many files were newly indexed, how many were skipped as unchanged, and the top three topics by total count. Nothing else.
