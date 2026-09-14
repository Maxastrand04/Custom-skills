---
name: lecture-preview
description: Turn one lecture deck into a one-page formula sheet before the lecture.
disable-model-invocation: true
---

# lecture-preview

One deck in, one **sheet** out. The sheet holds every formula that deck introduces, each with its symbols named and one line saying when you reach for it.

The user scans this sheet while working exercises. Nobody reads it front to back, so prose is dead weight.

Scope is this deck alone. A formula the course introduced three weeks ago stays off the sheet even when this lecture leans on it hard.

Invoke `unslop` for the prose.

Invoke `science-output` for every expression, in the sheet and in chat. It owns the `$$`-block rule and the inline-math ban.

## Step 1: Locate the deck

The deck's folder is normally `Lectures/`, and the course root is that folder's parent.

```
CourseRoot/
├── Lectures/           the deck
├── Exercises/          optional, the source of worked examples
└── Lecture-notes/      output, created if missing
```

Never read above the course root or outside it. Output is `Lecture-notes/<deck-filename>-preview.md`, rewritten whole on every run.

Ask here or not at all. Once writing starts the run is one-shot.

**Done when:** the deck path and the output path are both fixed.

## Step 2: Read every page of the deck

The Read tool caps a PDF at 20 pages per call and needs an explicit `pages` range past 10. Get the page count first, then read consecutive batches until the last page is covered.

A missed page is a missed formula, and a formula sheet with a hole in it is worse than none, because the user stops checking.

**Done when:** the highest page read equals the deck's page count. Every page.

## Step 3: Pull the formulas

For every formula the deck states, record four things and stop there:

- its name, in the lecturer's words where they name it
- the formula in LaTeX
- what each symbol means
- the slide it is stated on, and the slide it is worked on if the deck works it

Include the ones stated in passing on a summary slide. Skip only algebraic intermediate steps inside a derivation, which are not formulas anyone would reach for.

**Done when:** every formula in the deck carries all four fields, in deck order.

## Step 4: Write the sheet

```markdown
# Eigenvalues and diagonalization

> `Lectures/w03.pdf` · 2026-09-10

The lecture builds up to diagonalizing a matrix, so that raising it to a power becomes
raising numbers to a power. Everything before slide 20 is machinery for that.

## Characteristic polynomial · slide 12 · worked on slide 14

$$
\det(A - \lambda I) = 0
$$

A is the square matrix, lambda is an eigenvalue, I is the identity of the same size as A.

Reach for it when a question hands you a matrix and asks for its eigenvalues.

## Diagonalization · slide 21

$$
A = P D P^{-1}
$$

...
```

Hold the length with three rules:

- The intro is at most three sentences, and says what the lecture is doing rather than listing its topics.
- Each formula gets one symbol line and one "reach for it when" line. No second paragraph, no derivation, no worked example, no analogy.
- A formula that genuinely needs a caveat gets one more sentence. One. If most formulas on a sheet needed one, the rule was ignored rather than met.

A deck that states no formulas gets the intro and a line saying so. Do not manufacture formulas out of definitions to fill the sheet.

Then check the math rule:

```bash
grep -n '\$' "Lecture-notes/<deck-filename>-preview.md" | grep -v ':\$\$$'
```

Every line it prints is inline math that slipped through. Rewrite it and run it again.

**Done when:** every formula from step 3 has a section in deck order, no section runs past its symbol line and its reach-for line plus at most one caveat sentence, and the grep returns nothing.

## Step 5: Report

Say where the sheet is and how many formulas it holds. Then say the user can ask for a worked example of any formula on it. Two sentences.
