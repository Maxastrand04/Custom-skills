---
name: write-formula-sheet
description: Write formulas.md and formula-derivations.md for a course from its lectures, exercises, and exams.
disable-model-invocation: true
---

# write-formula-sheet

Build the cheat sheet for a course. Every formula the material states, grouped so the ones you use together sit together, each pointing at the slide it came from and at its derivation.

There is no manifest and no hashing. **The sheet is the state.** A re-run reads the course material again, reads the sheet it wrote last time, and adds what is missing. That is why every entry carries a source pointer. Without it, a re-run cannot tell a formula it already has from one it has not seen.

A cheat sheet you cannot navigate under exam pressure is worthless, so grouping is not decoration. Nothing is ever appended to the bottom.

Invoke `unslop` for the prose in both files.

## The two files

Both live at the course root, both are written whole on every run, both are owned by this skill. The user does not hand-edit them.

- `formulas.md` is the sheet. Groups of formulas, each entry stated, glossed, and pointed at its source.
- `formula-derivations.md` holds one section per formula in the sheet, with the derivation the course material gives. Where the material states a formula without deriving it, the section says so and names where it is stated. **Never derive a formula yourself.** A derivation the lecturer never gave is a derivation the student will not recognise on the exam, and it invites quiet mathematical errors into a file you will trust.

## Step 1: Locate the course

Run from the course root, or resolve it from wherever the user pointed. The layout matches the other course skills:

```
CourseRoot/
├── Lectures/                 slide decks, the primary source
├── Exercises/                optional, source and evidence of what is asked
├── Exams/                    optional, source and evidence of what is asked
├── course-index.md           optional, written by `course-index`, read only
├── formulas.md               output
└── formula-derivations.md    output
```

Never read above the course root or outside it. `Lecture-notes/` is derived from the decks, so it is not a source and gets skipped.

Stop and say so when `Lectures/` is absent and neither `Exercises/` nor `Exams/` holds a PDF. There is nothing to read.

**Done when:** the course root is resolved, both output paths are fixed, and every source PDF is enumerated and labelled lecture, exercise, or exam.

## Step 2: Read the sheet you already have

Missing `formulas.md` means this is the first run and the known set is empty.

Present means this is a re-run. Read it, and read `formula-derivations.md` beside it. Record the canonical name, the source pointer, and the group of every formula in it, plus every name in the `## Not examined` list. That set is what you already know; anything in the material that is not in it is what this run adds.

**Done when:** the known set is recorded, each entry with its name, source, and group, or the run is confirmed as a first run.

## Step 3: Read the material

Read every source PDF end to end. The Read tool caps a PDF at 20 pages per call and needs an explicit `pages` range past 10, so get the page count first and read consecutive batches until the last page is covered.

For each formula the material states, write down:

- What it is called, in the lecturer's own words where they name it
- The formula itself, in LaTeX
- What each symbol means, one line each
- When the student reaches for it, one line, phrased as the situation that calls for it rather than as a restatement of the formula
- Where it came from, as `Lectures/w03.pdf p12`
- Whether the material derives it, and on which pages

A formula stated only inside an exam or exercise sheet still counts. Those are often the ones nobody wrote on a slide and everybody is expected to know.

**Done when:** the highest page read equals the page count for every source PDF, and every formula found carries all six fields. Not "the important pages are covered". Every page.

## Step 4: Give every formula one canonical name

Left alone, one formula appearing in three lectures becomes three entries, and every re-run adds a fourth spelling of something already on the sheet.

So match each formula against the names already in the known set before minting a new one. Two formulas are the same when they compute the same thing, even when the notation differs, the constants are rearranged, or one is a special case written out in full. A special case that the course treats as its own named result is its own entry, cross-referenced to the general form.

Reuse the existing name whenever the underlying formula is the same. Where a re-run finds a better statement of a formula it already has, such as a cleaner form or a fuller symbol gloss, update the entry in place and keep both source pointers.

**Done when:** every formula found in step 3 is either matched to a known name or deliberately given a new one, and no two names refer to the same formula.

## Step 5: Rank against the exams

Read `course-index.md` when it exists. Never write to it.

Its topic frequency table decides what earns a place on the sheet. Map each formula to the canonical topic that covers it, then:

- A formula whose topic appears in `Exams` goes on the sheet, and its group sorts by that topic's exam count, descending. The high-yield material is at the top of the page.
- A formula whose topic appears in `Exercises` only goes on the sheet, below every examined group.
- A formula whose topic appears in neither goes to the `## Not examined` list at the bottom, one line, name and source only. It is not deleted, because a re-run with no record of it would find it again, add it again, and cut it again on every run.

With no `course-index.md`, every formula goes on the sheet, groups sort in course order, and the `## Not examined` list is left out. Say in the report that ranking was unavailable.

**Done when:** every formula is assigned to the sheet or to the not-examined list, and every sheet formula's group has an exam count behind its ordering.

## Step 6: Group the formulas

A group is a set of formulas the student would reach for in the same question. Not a chapter of the course. Name the group for the situation it serves, so scanning the headings under exam pressure gets you to the right block without reading the formulas.

Regroup the whole sheet on every run. A new formula that belongs beside three existing ones goes beside them and the group is rewritten around it. New material that splits an overgrown group into two well-named ones is a good outcome, not churn.

A group of one is fine when the formula genuinely stands alone. A group named `Miscellaneous`, `Other`, or `Additional formulas` is a failure of this step, and every formula in it needs a real home.

**Done when:** every sheet formula sits in exactly one named group, no group name is a synonym for "leftovers", and every group name says when you would open it.

## Step 7: Write both files

Write `formulas.md`, rebuilt whole:

```markdown
# Formulas

> Written by the `write-formula-sheet` skill. Re-run it after adding material.
> Sources: <N> lectures, <M> exercise sheets, <K> exams · <YYYY-MM-DD>
> Ranked against course-index.md.

## Eigenvalue problems
_Exams: 5_

### Characteristic polynomial

$$\det(A - \lambda I) = 0$$

- $A$ — the square matrix
- $\lambda$ — an eigenvalue
- $I$ — identity, same size as $A$

Use when: you need the eigenvalues of a matrix given only its entries.
Source: `Lectures/w03.pdf` p12 · [Derivation](formula-derivations.md#characteristic-polynomial)

### Eigenvector from an eigenvalue
...

## Not examined

- Frobenius companion matrix — `Lectures/w03.pdf` p31
```

Then write `formula-derivations.md`, one section per sheet formula, in the same order:

```markdown
# Formula derivations

> Written by the `write-formula-sheet` skill. Derivations are the course's own.

## Characteristic polynomial

From `Lectures/w03.pdf` pp10-12.

A non-zero $v$ with $Av = \lambda v$ gives $(A - \lambda I)v = 0$, so
$A - \lambda I$ has a non-trivial null space, so its determinant is zero.

## Frobenius norm

Not derived in the course material. Stated at `Lectures/w05.pdf` p4.
```

Every anchor linked from `formulas.md` must resolve to a section that exists. Formulas in the `## Not examined` list get no derivation section.

**Done when:** both files are written, every sheet formula has a derivation section, every derivation link resolves, and every formula recorded in step 4 appears in exactly one of the sheet or the not-examined list.

## Step 8: Report

Say how many formulas the sheet now holds, how many this run added, how many groups exist and which regrouped, how many formulas went to the not-examined list, and how many sections say the course never derives the formula. Nothing else.

**Done when:** the report states all five counts and nothing else.
