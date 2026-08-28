# Teaching one topic

Reached from [`SKILL.md`](SKILL.md) when the notes file already exists. One topic, then the session ends.

Invoke `talk-to-highschooler` for the opening explanation and `unslop` for anything written to the file. Both bend to whatever the user needs instead; the level that makes it click wins over the default level.

## Inline math is banned

Holds everywhere in this skill, in the notes file and in chat. It is the rule most likely to slip, because writing `$x$` mid-sentence is a reflex, so check it deliberately rather than trusting that you followed it.

**A line containing a single `$` is a bug.** Dollar signs appear only as a `$$` fence, alone on its own line, with a blank line above and below. Every other inline form is banned too: `$...$`, `\( ... \)`, and LaTeX wrapped in backticks.

There is no exception for a short expression, a single variable, or a Greek letter. Short inline math is exactly what produces the unreadable output, since a paragraph broken up by a dozen dollar signs is harder to read than one that says the same thing in words.

Three cases cover every temptation:

| Reflex | Write instead |
|---|---|
| the vector `$v$`, `$n$` grows | the vector v, n grows. A bare Latin letter is written bare, with no markup at all |
| `$\lambda$`, `$\epsilon \to 0$` | lambda, as epsilon shrinks to zero. Greek letters are spelled out in Latin letters |
| `$O(n^2)$`, `$\frac{1}{2}mv^2$` | anything with structure, meaning a fraction, exponent, subscript, operator, or relation, is either said in words ("quadratic in the number of items") or moved into a `$$` block of its own |

Every block gets its symbols named in words directly under it. An unnamed formula teaches nothing.

```markdown
The error shrinks with the square of the step size, so halving the step cuts the error to a quarter.

$$
E = C h^2
$$

E is the error, h is the step size, and C is a constant that depends on the function but not on h.
```

**Check it, do not trust it.** After writing to the notes file, run this against it:

```bash
grep -n '\$' "<path to notes file>" | grep -v ':\$\$$'
```

Every line it prints is inline math that got through. Rewrite each one by the table above and run it again. A clean run is the only evidence that the rule held.

## Step 1: Load one topic and nothing else

Scan the notes file for the first metadata line still reading `Not covered yet.` That heading is this session's topic, and its slide range is the whole reading list.

Load three things and stop there.

- The topic's slide range from the deck. Not the rest of the deck.
- The span of `Lecture-notes/.transcripts/<deck-filename>.srt` covering those slides, if a transcript exists. The "Using it" section of [`transcript.md`](transcript.md) says how to line it up against the slides and why the deck, never the transcript, spells the terminology.
- The finished topics above this one in the notes file. They are what the user already understands, and every one of them is available to build the next explanation on.

The transcript is yours to teach from. Quote what the lecturer said when it explains something the slide skips, and tag it `[🎙 mm:ss]` if it reaches the file.

**Done when:** the topic is identified, its slides are read, and the matching transcript span is located or confirmed absent.

## Step 2: Explain it once

Open with the shortest honest explanation of the topic. Name every domain word in plain words the first time it appears. No slide-bullet recopying, no preamble about what you are about to cover.

Then hand it over and find the edge of what landed. Ask what part is unclear, or ask the user to say back what they think is going on. Never ask "does that make sense?" Everyone says yes to that question and it tells you nothing.

**Done when:** the user has said something about the topic in their own words, however wrong or partial.

## Step 3: Pick the move that fits the gap

Their answer says where the confusion sits. Aim at that spot and pick the move it calls for:

- **Derive it.** For a formula that arrived out of nowhere. Build it from something they already accept, one step at a time, and let them predict the next step.
- **Draw a parallel.** For a mechanism with no intuition attached. Find a thing outside the subject that works the same way, then say where the parallel breaks, because an analogy nobody has bounded gets over-trusted.
- **Link it back.** For something that looks new but is not. Point at a finished topic in this file, or another course, and show it is the same shape.
- **Drop the level.** For a definition stacked on three other definitions. Strip it to the crudest version that is still true, get agreement there, then add the precision back one layer at a time.

One move at a time. Ask again, and if the gap moved, pick the move that fits the new one. If the same explanation is not landing on the second pass, the move is wrong, not the wording; switch moves rather than repeating yourself louder.

A topic carrying `**[high-yield]**` gets pushed harder, since it is on the exam. Push past the first plausible answer on those.

**Done when:** the user asks to be tested, or claims they have it.

## Step 4: Teach-back

A claim of understanding is not the gate. The user explains the topic in their own words, with the explanation out of view. Not repeating the phrasing back. If it comes back as the same sentences you said, it is recall, and recall is not the gate.

Ask for the picture, not the definition. How do you see it, what is actually going on, what is moving. That answer is the note itself, word for word, so capture their phrasing as they say it rather than reconstructing it later from memory.

**Then try to break it.** A picture in the user's own words is fluent by construction, and fluent is not the same as right. Read it back against the deck and hunt for the point where the two diverge. Separate two failures:

- **Crude but true.** It leaves things out, or sits below the deck's precision, and everything it does claim holds. This passes, and the note sits at that level and says so.
- **Wrong.** It contradicts the deck, or it is an analogy carried past the point where it stops working. This does not pass, however well it was said.

Break it by prediction, not by correction. Find the case where their picture and the deck give different answers, pose it, and let them answer from their picture. Watching their own picture produce the wrong answer is what makes the fault real to them. Being told they are wrong just gets your sentence copied back. Then return to step 3 with the move that fits.

Say the divergence out loud even when the session has run long and they sound finished. A wrong picture written into the file is worse than no file, because they will revise from it for the rest of the course.

Where it comes back thin, name the specific part that was thin, go back to step 3, and aim the next move there. A thin teach-back writes a thin note.

**Done when:** the user's picture stands on its own, it survived the prediction aimed at breaking it, and their wording of it is captured.

## Step 5: A real exercise

Then they work a question from the course's own `Exercises/`. Never one you wrote. An invented question tests the explanation you just gave, because you wrote both, and the course's own questions are the ones the exam is drawn from.

**Work out what is unlocked.** Two things combine:

- **Covered topics.** Every metadata line across every file in `Lecture-notes/` whose status reads `Covered`, collecting the names on its `Indexed as` field. The whole folder, not this lecture. A question on today's topic usually needs something from three weeks ago, and looking only at this file would call that unmet.
- **The prerequisites table** in `course-index.md` at the course root, which lists what each question requires.

A question is unlocked when this topic is among its requirements and every other requirement is already covered. Pick one of those, favouring a question that leans on the topic rather than mentioning it in passing. Open the sheet and pose the question as written.

**Nothing unlocked is a normal outcome.** When every question on this topic still needs a topic from a later lecture, the topic closes without one and records what it is waiting on. Do not reach for an exam question instead, and do not invent one. Ask one transfer question so the topic still closes on something, meaning a question that changes a condition or drops an assumption and cannot be answered by finding the matching slide. Then say plainly which questions are waiting and on what.

Same fallback when `Exercises/` does not exist, or when `course-index.md` does not exist. In the second case say so once and recommend running `course-index`.

**Working it.** They attempt it. You check the work. A wrong turn is the most useful thing that will happen this session, so name where it went wrong and send them back into it rather than finishing the question for them. Handing over the answer at the first stumble turns the gate into a demonstration.

**Done when:** an unlocked exercise is worked to a correct answer the user reached, or the topic is recorded as waiting and one transfer question has passed.

## Step 6: Write the topic

**The note is the user's picture of the topic and nothing else.** They just explained it. That explanation, in their words, is the whole body. Not a fresh summary in your voice, not the deck reworded, not the parts they never reached.

Test every sentence before it goes in: did they say this, or something near enough that they would read it back as theirs? If not, cut it. The file exists to restart their own thinking six weeks from now, and only their own words do that. A textbook paragraph on the same topic is already in the deck.

So keep what they built with. The crude parallel that finally worked stays, even where the deck is more precise. A level below where the deck pitches it stays, and the note says it is sitting low. A wrong first guess stays where correcting it is what made the right answer land. Sharpen their wording by cutting repetition and finishing half-sentences. Never by raising its register.

Where they never got to something the deck covers, the note stays silent on it or names it under **Still shaky**. Do not fill the gap. Coverage is not what this file is for.

Update the metadata line's status from `Not covered yet.` to `Covered <YYYY-MM-DD>.` and write the body under it:

```markdown
## 3. Eigenvectors (slides 12-20)
> Indexed as: Eigenvalues and eigenvectors · **[high-yield]** 4 of 7 past exams · Covered 2026-08-27.

**Clicked by** deriving it from the definition of a linear map, one step at a time.

<Their picture of the topic, in their own words, as prose. Nothing in here that they did
not say. I kept thinking of the noise as something to remove, but the lecturer treats it as
the point [🎙 24:10].>

**Formula.** In a `$$ ... $$` block, symbols named in words right under it.

**Exercises.** sheet-03 Q2, done. First pass scaled the vector instead of leaving it alone,
which is the thing to watch for.

**Still shaky.** Why the normalization constant is there. Ask at recitation.
```

Rules for the body:

- The **Clicked by** line is the refresher hook. Name the move and what it was built on, in one sentence, so re-reading it six weeks later restarts the same path.
- **Exercises** names every question worked and what the mistake was, since the mistake is the part worth re-reading. When nothing was unlocked, it reads `None unlocked yet, sheet-04 Q3 is waiting on <topic>` instead.
- Prose, not bullets. A bullet list mirroring the slide's bullet list has added nothing.
- Math in `$$ ... $$` blocks only. Run the inline-math grep from the top of this file over the notes file once the body is written, and fix every line it prints.
- A diagram only reaches the file when the user's picture leans on it, described the way they described it, since the file holds no images.
- No naked terms. Any domain word gets a plain-words gloss in the sentence it first appears in. Where they used the word without ever unpacking it, ask them for the gloss at step 4 rather than supplying your own.
- `[🎙 mm:ss]` tags a line from the video that the user took up as their own. A lecturer's phrasing they never adopted is not part of their picture and does not reach the file.
- **Still shaky** only when something genuinely is. An empty one is noise.

Then bump the progress line at the top of the file.

**Done when:** every sentence in the body traces back to something the user said, the inline-math grep returns nothing, the status reads `Covered`, and the progress count matches.

## Step 7: Spend what this topic unlocked

Covering this topic may have completed the requirements of questions held back under earlier topics, including topics in other lectures. Do them now, while the topic is warm. Waiting until revision means the sheet gets read once, cold, with nothing recent to attach it to.

Search `Lecture-notes/*.md` for `waiting on`, and check each of those questions against the covered set as it now stands. Every requirement met means it is unlocked.

Work them the same way as step 5, one at a time, until they run out or the user stops. Each one that gets done is recorded under this topic's **Exercises** line, and the older waiting note that named it is replaced with a pointer to where it was worked. Anything unlocked but not attempted stays named in the file so it is not lost.

**Done when:** every `waiting on` note in the folder has been rechecked, and each is either worked and recorded, still waiting on a named topic, or listed as unlocked and not yet attempted.

## Step 8: Report and stop

Name the topic just written, the exercises worked, the count of topics remaining, and what the next topic is. Then stop. The next topic is a fresh invocation with a fresh context window, which is the point of one topic per session. Carry on into the next topic only if the user asks.
