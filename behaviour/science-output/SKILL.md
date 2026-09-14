---
name: science-output
description: >
  Put every expression in a $$ block with its symbols named underneath, and at
  most three sentences that say why the step happened rather than restating it.
  Use whenever output carries a formula, a derivation, a worked calculation, or
  a unit conversion, in any quantitative subject, and whenever another skill
  writes math into a file.
---

# science-output

The format rules for output carrying math. Physics, chemistry, math, engineering, anything with an expression in it.

This skill owns format only. It does not decide what gets explained, at what level, or how long the answer runs.

## Inline math is banned

Holds in files and in chat. It is the rule most likely to slip, because writing `$x$` mid-sentence is a reflex, so check it deliberately rather than trusting that you followed it.

**A line containing a single `$` is a bug.** Dollar signs appear only as a `$$` fence, alone on its own line, with a blank line above and below. Every other inline form is banned too: `$...$`, `\( ... \)`, and LaTeX wrapped in backticks.

There is no exception for a short expression, a single variable, or a Greek letter. Short inline math is exactly what produces the unreadable output, since a paragraph broken up by a dozen dollar signs is harder to read than one that says the same thing in words.

Three cases cover every temptation:

| Reflex | Write instead |
|---|---|
| the vector `$v$`, `$n$` grows | the vector v, n grows. A bare Latin letter is written bare, with no markup at all |
| `$\lambda$`, `$\epsilon \to 0$` | lambda, as epsilon shrinks to zero. Greek letters are spelled out in Latin letters |
| `$O(n^2)$`, `$\frac{1}{2}mv^2$` | anything with structure, meaning a fraction, exponent, subscript, operator, or relation, is either said in words ("quadratic in the number of items") or moved into a `$$` block of its own |

## Keep the LaTeX readable as source

Most of this output is read in a terminal, where nothing renders and a `$$` block arrives as raw source. Use only what survives unrendered.

Banned, because their only job is typesetting: `\underbrace`, `\overbrace`, an `aligned` block used to hang a `\text{}` annotation column beside the math, `\left`/`\right`, `\displaystyle`, spacing macros, colour.

Fine, because there is no plainer way to say the thing: fractions, exponents, subscripts, roots, integrals, sums, Greek commands, `\cdot`, `\text{}` for units and short labels, and `aligned` when several equations genuinely line up on their equals signs.

The test is whether a reader who cannot see it rendered still gets the expression.

Justifications go in the prose under the block. Never inside it.

## Show the substitution

An expression explains itself when the quantities are already sitting in it. Write the step with the real numbers and units in place rather than stating the general form and following it with a sentence about what to plug in.

Units stay inside the block and cancel where the reader can watch them cancel. Dropping units through the working and reattaching them to the answer is the fastest way to make a physical calculation unfollowable.

```markdown
$$
v = \sqrt{2 \cdot 9.81 \, \text{m/s}^2 \cdot 1.5 \, \text{m}} = 5.4 \, \text{m/s}
$$
```

## Name the symbols, then three sentences

Directly under every block, name what each symbol means, in words. An unnamed formula teaches nothing.

Then at most three sentences. The symbol line does not count against them.

**Those sentences say why this step happened, never what the block says.** Restating the algebra in prose is the padding this cap exists to kill.

The test: if a sentence would still be true with different numbers in the block above it, it is describing the machinery instead of the move. Cut it.

> Bad: Here we take the square root of the product of two times the acceleration due to gravity and the height, which gives us the velocity.
>
> Good: Energy conservation gives the speed directly, so the mass never enters and the drop time is never needed.

Where a block genuinely needs a fourth sentence, split it into two blocks instead. If most blocks in an answer needed a fourth, the rule was ignored rather than met.

## Checking a file

Chat output gets no check. A file does, and the skill writing it runs this against the path it just wrote:

```bash
grep -n '\$' "<path>" | grep -v ':\$\$$'
```

Every line it prints is inline math that got through. Rewrite each one by the table above and run it again. A clean run is the only evidence that the rule held.
