---
name: example-workthrough
description: Works one example of a topic end to end, opening with the theory and formulas it will use.
disable-model-invocation: true
---

# example-workthrough

One example, worked in full, so the user gets an idea of a topic they have not met yet.

It opens with the **kit**, meaning the theory or principle in play and the formulas the example will use. Then it works the example.

Invoke `science-output` for every expression. Answer in chat and **never write to a file**, whichever skill invoked this.

Bind no reading level. Pitch it wherever the user's question sits. If they want it lower they type `eli10` or `eli5` alongside.

## Step 1: Pick the example

**No course folder in play** -> invent the smallest case that exercises the principle. Do not go hunting the filesystem for a course, and do not ask which course this is. Most invocations are a cold topic with no folder behind them, and stalling to ask fails that case to serve a rarer one.

**A course folder already in play**, because `lecture-preview` invoked this or the conversation established a course root -> take the example from the course's own material, in this order: a worked slide in the deck, then a question in `Exercises/`. Only when neither has one, invent the smallest case.

Either way, name the source in one line. `sheet-03 Q2`, or `slide 14`, or `invented`. The user should always be able to tell whether they are looking at the course's own question or one that was made up.

**Done when:** the example is chosen and its source is named.

## Step 2: Lay out the kit

One line naming the theory or principle. Then each formula the example will use, as a `$$` block with its symbols named underneath and one line on the condition where that formula applies.

The condition line is the part that makes a topic click and the part a worked example always drops. The ideal gas law needing a gas far from condensing, the small-angle approximation needing radians and a small angle, the kinematic equation needing constant acceleration.

**Every formula in the kit must appear again in the worked steps.** No survey of the topic, no related results the user might meet later, nothing listed for completeness. If the example does not use it, it is not in the kit.

That cap means the kit cannot show the general form of a result the example only uses a special case of. Correct. The general form belongs on a formula sheet.

A domain term first appearing here gets a plain-words gloss in the sentence it appears in, because the kit is where the user decides whether they can follow the rest.

**Done when:** the kit names its principle, every formula in it is one the example will use, and no term in it is used before it is glossed.

## Step 3: Check the floor, in one question

Ask which of the listed formulas is new to them.

Not whether it makes sense, and not whether they understand it. Everyone says yes to those and they tell you nothing. "Which of these is new" has a real answer, including "none", and "none" costs one word.

Do not guess which one they will struggle with. Guessing wrong and explaining the easy one is worse than not asking.

Anything they name gets explained before the example starts. Silence or "go" means continue.

**Done when:** the user has answered, or waved it through.

## Step 4: Work it

Numbered steps. The arithmetic is visible at every one, so the method can be copied against a different question.

**No step jumps.** Where one line becomes another, the operation that got it there is visible, either in the expression or in the sentence under it. The failure mode of a worked example is the step that quietly does three things at once, and that is always the step the user was stuck on.

No theory beyond the kit, and no restating what a formula means. That work is done.

The result is whatever the example produces: a number with units, a closed form, a proved statement, a named product. Not every example ends in a number, and one should never be manufactured to look finished.

**Done when:** the example runs from the question to a stated result, and every step shows the work that produced it.

## Step 5: Name the trap, then stop

One line on the step people get wrong here, and what going wrong looks like.

That is the highest-value sentence in a worked solution and the reason the whole thing was worth reading.

Then stop. No teach-back, no "now you try one", no checking whether it landed. `lecture-notes` owns gating, and it gates on a real question from `Exercises/`. A second, weaker gate here would only compete with it.
