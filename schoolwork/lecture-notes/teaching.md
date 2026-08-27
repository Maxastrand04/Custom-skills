# Teaching one topic

Reached from [`SKILL.md`](SKILL.md) when the notes file already exists. One topic, then the session ends.

Invoke `talk-to-highschooler` for the opening explanation and `unslop` for anything written to the file. Both bend to whatever the user needs instead; the level that makes it click wins over the default level.

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

Where it comes back thin, name the specific part that was thin, go back to step 3, and aim the next move there.

**Done when:** the teach-back stands on its own.

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

**The teach-back is the draft.** They just said the thing that works for them; write that down, sharpened, not a fresh summary in your own voice. If the parallel that unlocked it was theirs, the parallel goes in the file. If it clicked at a cruder level than the deck pitches it, the file sits at that cruder level and says so.

Update the metadata line's status from `Not covered yet.` to `Covered <YYYY-MM-DD>.` and write the body under it:

```markdown
## 3. Eigenvectors (slides 12-20)
> Indexed as: Eigenvalues and eigenvectors · **[high-yield]** 4 of 7 past exams · Covered 2026-08-27.

**Clicked by** deriving it from the definition of a linear map, one step at a time.

<The explanation, in the user's framing, as prose. Where a step was the thing that unlocked
it, keep the step. Where a wrong first guess is what made the right answer land, keep the
wrong guess and say why it fails. The lecturer said the noise is a feature, not a bug
[🎙 24:10].>

**Formula.** Every symbol named in words, right under it.

**Exercises.** sheet-03 Q2, done. First pass scaled the vector instead of leaving it alone,
which is the thing to watch for.

**Still shaky.** Why the normalization constant is there. Ask at recitation.
```

Rules for the body:

- The **Clicked by** line is the refresher hook. Name the move and what it was built on, in one sentence, so re-reading it six weeks later restarts the same path.
- **Exercises** names every question worked and what the mistake was, since the mistake is the part worth re-reading. When nothing was unlocked, it reads `None unlocked yet, sheet-04 Q3 is waiting on <topic>` instead.
- Prose, not bullets. A bullet list mirroring the slide's bullet list has added nothing.
- Every formula gets its symbols named. An unexplained formula is a picture.
- A diagram the deck shows gets described in words, since the file holds no images.
- No naked terms. Any domain word gets its plain-words gloss in the sentence it first appears in.
- `[🎙 mm:ss]` tags anything that came from the video and is not on the slides. Nothing else is tagged, because everything else is the user's own account.
- **Still shaky** only when something genuinely is. An empty one is noise.

Then bump the progress line at the top of the file.

**Done when:** the section is written, the status reads `Covered`, and the progress count matches.

## Step 7: Spend what this topic unlocked

Covering this topic may have completed the requirements of questions held back under earlier topics, including topics in other lectures. Do them now, while the topic is warm. Waiting until revision means the sheet gets read once, cold, with nothing recent to attach it to.

Search `Lecture-notes/*.md` for `waiting on`, and check each of those questions against the covered set as it now stands. Every requirement met means it is unlocked.

Work them the same way as step 5, one at a time, until they run out or the user stops. Each one that gets done is recorded under this topic's **Exercises** line, and the older waiting note that named it is replaced with a pointer to where it was worked. Anything unlocked but not attempted stays named in the file so it is not lost.

**Done when:** every `waiting on` note in the folder has been rechecked, and each is either worked and recorded, still waiting on a named topic, or listed as unlocked and not yet attempted.

## Step 8: Report and stop

Name the topic just written, the exercises worked, the count of topics remaining, and what the next topic is. Then stop. The next topic is a fresh invocation with a fresh context window, which is the point of one topic per session. Carry on into the next topic only if the user asks.
