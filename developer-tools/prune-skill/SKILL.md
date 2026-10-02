---
name: prune-skill
description: Prunes a skill after it is written or changed. Takes a cold read of what it does, checks its leading words, cuts it against a fixed list of smells, then takes a second cold read to prove the meaning survived.
disable-model-invocation: true
---

# prune-skill

**A skill grows by addition and shrinks only on purpose.** Every line has to earn the context it costs, and the burden is on the line, not on the cut.

Prune, don't rewrite. The skill's job and its author's judgement stay, and you prove it by having someone cold read the skill before the cuts and again after. The two cold reads have to say the same thing.

---

## 1. Take the target

The argument is a skill name or a path. No argument means ask which skill, and stop until told. Never guess from recent work, and never scan a repo for something that looks freshly edited.

Read the `SKILL.md` in full, then every file it references, then check that each reference resolves.

**Completion criterion:** the `SKILL.md` and every bundled file it names read end to end. Judging a skill on its headings is how sediment survives a pruning.

## 2. Take a cold read

A cut is safe when the skill still says the same thing, and you cannot judge that from inside your own head, having just decided what to remove. Get an outside read first.

Spawn a subagent, hand it the `SKILL.md` and every bundled file, and have it answer seven questions in order.

1. What is this skill for?
2. What fires it?
3. What are its steps, in order?
4. What does it require, and what does it forbid?
5. Where does it stop for the user?
6. What does it produce?
7. Which word does the skill repeat to steer you, and what does that word make you do? Answer "none" if no word does that.

Those answers are the **cold read**. Record them verbatim.

Do not tell the subagent that a prune is coming, do not name the lines you suspect or the leading word you expect, and do not hand it your own summary. A cold read that echoes you proves nothing.

**Completion criterion:** a recorded cold read answering all seven questions.

## 3. Find the leading words

A **leading word** is one word the skill names once, repeats everywhere, and uses to steer the agent. The model already holds a concept for the word, so the word carries behaviour a paragraph would otherwise have to spell out. "Prune" is the leading word of this skill. Leading words steer a skill more than any other line, so they get their own pass.

Take the purpose from cold-read question 1, never from your own read of the skill.

- **List every candidate.** A term the skill bolds, defines, or repeats as a handle. Count its uses. A word used once leads nothing.
- **Check each against question 7.** When the cold reader named a different word, or took the right word to mean something else, the word is misfiring. Propose a reshape: a sharper word, a definition at first use, or cutting the rival term.
- **Check each against question 1.** A leading word that steers toward something other than the purpose is leading the agent somewhere else.
- **Collapse restatements.** Three adjectives circling one quality, or one idea under several names, want one word. Show the current text, the proposed word, and every site it would replace.
- **When the skill has none,** recommend whether to add one, with the reason. A skill whose steps already carry its purpose can do without. When one would help, propose the word, its definition line, and every site it would appear.

Every finding in this step is a proposal. Never apply one on your own judgement, because a wrong word changes what the skill means. An approved added or changed leading word is a change the user accepted, and step 9 treats it as one.

**Completion criterion:** every candidate listed with its use count and checked against questions 1 and 7, and a verdict for the skill: keep, reshape, collapse, add, or none needed, with the reason.

## 4. Pass it against the smells

Nine smells follow. Take them one at a time over the whole file, and run each on sentences in isolation, not on paragraphs, because a paragraph averages out and a dead sentence hides inside a live one.

**No-op.** The line describes what the agent would do anyway. Strike the sentence and ask whether behaviour changes. "Be careful", "consider the context", "make sure the code is correct" all fail. So does a weak intensifier propping up a habit the agent already has. Delete the whole sentence rather than tightening its wording.

**Duplication.** The same meaning in two places, so both copies have to change together. Pick the one authoritative site, keep it, and cut the rest. A rule restated in the description and again in the body is the common case.

**Sediment.** A layer that made sense against a version of the skill that no longer exists. Look for instructions about a step that was removed, a format nothing writes any more, a caveat about a branch that got split out.

**Sprawl.** The skill is simply long, even where each line is live. Ask whether a block is reference every run needs, or reference only some runs reach. The second belongs in a bundled file behind a pointer. Ask also whether one skill is doing two jobs that never run together.

**Naming.** A skill must work for any agent, any model, any user, any project. Findings: a named model or vendor, a person's name, first-person owner voice, an assumption about one machine, one directory layout, or one team's habits. Address the agent as "you" and the human as "the user". Naming a tool the skill actually drives is fine.

**Fuzzy completion.** A step that ends on a condition the agent cannot check. "Produce a list of changes" cannot be verified done; "every modified file accounted for" can. Fuzzy endings invite the agent to declare victory early.

**Explanation past the instruction.** Rationale that keeps going after the agent already knows what to do. One line of why buys reliable execution. Four lines of why buys nothing and reads as an essay. Cut to the sentence that changes the action.

**Relevance.** The line is alive, unique, and true, and still has nothing to do with what this skill does. Cut it.

**Pointer drift.** A reference that resolves but whose wording no longer describes what is on the other end. The agent reaches the file, reads something else, and improvises.

**Completion criterion:** every smell above applied to the whole file, with a stated result for each, including the ones that found nothing. A pass that reports only what it happened to notice is not a pass.

## 5. Run it through `unslop`

A skill has to meet the `unslop` criteria like any other writing, and it is held to them harder, because its words are the machine rather than a description of one. Invoke `unslop` over the `SKILL.md` and every bundled file, and treat what it flags as findings in this session. If no such skill is installed, apply the four tells below directly.

Four tells do real damage in a skill and are worth hunting first:

- **Synonym cycling** breaks a leading word. If one idea appears as three names, the agent has three concepts instead of one and reaches for a different behaviour each run. Check every name against the leading words from step 3, and fold what you find into that step's findings.
- **Puffery, filler, and hedging** are no-ops that read as content. "It is important to carefully consider" is four words of tax on a sentence that has not started yet.
- **The rule of three** invents a third item to round out a pair, and in a skill that third item becomes an instruction the agent tries to follow. Use the natural number.
- **Feeling over mechanism.** "Keeps the code clean" is unrunnable. Name the check, the file, or the number the agent can act on.

Do not let the polish soften a directive. `unslop` prefers plain words; a skill also needs blunt ones. "Never edit the file" must survive the pass as "never", not soften into "avoid editing".

On a description, step 6 wins. A trigger list naming three distinct uses is not a rule of three, and cutting one to round the list down loses a trigger.

**Completion criterion:** the criteria applied to the `SKILL.md` and every bundled file, the flags folded into the one report, and no directive weakened on the way through.

## 6. Ask the invocation question

Every model-invoked skill puts its description in the context window on every turn, used or not. That is a standing tax, so the skill has to need what it buys.

It buys two things and nothing else. The agent can fire the skill on its own, and another skill can reach it by name. If neither is true, the description is pure load and the skill should be user-invoked. Set `disable-model-invocation: true`, and cut the description down to one human-facing line with the trigger phrasing stripped.

The cost of going user-invoked is real and lands on the user, who now has to remember the skill exists. Say that when you recommend it. When a user already carries too many, the answer is one skill that names the others, not putting descriptions back.

If the skill stays model-invoked, prune the description harder than the body. One trigger per distinct use. Synonyms renaming a single use are duplication. Identity already stated in the body is duplication.

**Completion criterion:** a stated verdict, model-invoked or user-invoked, with the reason naming which of the two things the description buys.

## 7. Report

One block, findings numbered, then stop and wait. Do not edit anything yet.

```
prune-skill  <target>
Read      SKILL.md + 2 bundled files, 1 pointer broken
Cold read recorded, 7 questions
Leading   2 found, 1 reshape, 0 add
Checked   no-op 4, duplication 2, sediment 1, sprawl 0, naming 1,
          fuzzy 0, explanation 0, relevance 0, drift 0
Unslop    1
Findings  10
Invocation  user-invoked, keep as is
```

Then each finding as: the quoted line or block, which smell or step, and the verdict. Cut, rewrite to this, or move to this file. Group findings that are one problem, so two copies of a rule are one finding and not two.

Lead with your own recommendation on each, including whether an added leading word is worth having.

**Clean is a valid report.** If the skill is tight, say so in the block and name what you checked. Never invent a finding to justify the session.

**Completion criterion:** the report emitted with a result stated for the leading words and every smell, and nothing edited.

## 8. Apply

After approval, all edits in one pass. Apply exactly what was approved, nothing adjacent that caught your eye on the way through.

**Completion criterion:** every approved finding applied.

## 9. Take a second cold read

Spawn a fresh subagent that has not seen the first cold read, and put the same seven questions to it against the pruned files. Reusing the first subagent gets you its memory instead of the text's meaning.

Compare the two cold reads question by question, on meaning. Wording will differ and that difference means nothing. A divergence is a purpose, trigger, step, rule, prohibition, gate, output, or leading word that the first cold read names and the second does not, or that the second invents. Steps that change order are a divergence.

For each divergence, find the cut that caused it. Name the cut, restore the line it removed, and take the cold read again. Keep the finding open in the report rather than arguing the new meaning is acceptable, because the user approved a prune and not a change.

A leading word the user approved in step 3 should show up in question 7. If the second cold read names a different word, or none, the new word is not steering yet. Report it as open rather than restoring the old text.

Some divergences have no causing cut, because two cold reads of one text will not match perfectly. Before you conclude that, diff the passage the answer covers and show it unchanged. Only then record it as variance. An unexplained divergence is a cut you have not found yet, so never reach for variance first.

**Completion criterion:** a second cold read answering all seven questions, compared to the first question by question, each divergence resolved by a restore, shown to be variance against an unchanged diff, or listed as a change the user accepted.
