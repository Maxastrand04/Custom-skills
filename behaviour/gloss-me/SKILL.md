---
name: gloss-me
description: >
  Gloss every naked term, a domain term missing from the user's personal glossary
  of known terms, before its first use, and ask once per response which new terms
  they are now comfortable with. Use whenever output is written for the user to
  read and act on.
---

# gloss-me

This skill owns which terms get glossed and the glossary file. It does not own the wording level or what work gets done. A wording skill such as `talk-to-highschooler`, when one is active, owns the level.

A **naked term** is a domain term the user doesn't know yet. To **gloss** a term is to define it in one clause, in a gloss block, before its first use. Gloss every naked term. Never ship one unglossed.

## The glossary

`~/.claude/glossary.md`. One file, for every project. No other skill writes it.

Confirm writes in one line, e.g. `Added to glossary: idempotent, upsert.`

Read it in full once per conversation, the first time this skill applies. Do not re-read it per response. If it is over 1,000 lines, skip the full read and instead run one batched check per response on the terms you are about to use, with the headings listed so each hit can be placed under one:

```bash
grep -n '^## ' ~/.claude/glossary.md; grep -niwF -e 'term one' -e 'term two' ~/.claude/glossary.md
```

If the file does not exist, the glossary is empty. Carry on with the floor alone and create the file on the first write.

Format: one line of bare terms per domain heading, comma-separated, no definitions. A short parenthetical only where the user's meaning differs from the standard one.

```markdown
# Known terms

## Programming
git, rebase, JWT, ORM, eager loading

## Physics
torque, "work" (the physics sense, force times distance)

## Project: my-app
Order ledger, Nightly sync
```

Two kinds of heading. A domain heading, like `## Programming`, holds terms that count as known everywhere. A project heading, `## Project: <project-name>`, holds vocabulary one project coined or uses in its own sense, and those terms count as known only inside that project. The project-name is the name of the repo's top folder, so `~/code/my-app` gives `my-app`. Outside a git repo, use the name of the working folder. A hit under another project's heading does not count.

Match a term by its meaning, not its exact spelling. `eigenvalues` is covered by `eigenvalue`, `rebasing` by `rebase`, and `JWT` covers `JSON Web Token`.

## The floor

Assumed known, use freely: arithmetic and algebra, percentages, ratios, powers, basic probability, reading a graph; variables, functions, loops, conditionals, lists, files, running a command.

That is the default. `talk-to-middleschooler` lowers it to nothing when active. The glossary sits on top of whichever floor applies.

## Naked terms

A term is not naked, and needs no gloss, if it is:

- on the floor,
- in the glossary, under a domain heading or the current project's heading, or
- glossed earlier in this conversation.

Nothing else counts. A project's `CONTEXT.md`, its ADRs, a project glossary, a README, or any other doc read in this conversation describes the project, not the user. A term defined there stays naked until the user says they're comfortable with it, and the doc's definition is a good source for the gloss's wording.

A naked acronym expands in its gloss.

## The gloss block

Glosses go in a block of their own, placed right before the first paragraph that uses any of its terms. A response can carry several blocks. Terms inside a table or code block get their gloss in a block before it.

Write the block exactly like this, as rendered markdown and never inside a code fence:

New terms
- **query**, a request the app sends to the database for some data.
- **N+1 query**, loading a list with one query and then running one more query per item in it.

A plain `New terms` line, then one dash item per term: the term in bold, a comma, a one-clause definition, a full stop. No tables, no inline code, no divider lines. They render unevenly across terminals.

**Chained glosses.** A gloss may lean on known terms and on terms glossed on the lines above it in the same block, nothing else. If a gloss needs another naked term, gloss that term on the line above first, the way `query` comes before `N+1 query`.

## The footer

End every response that glossed a naked term with one line listing every term glossed anywhere in that response:

> New terms this turn: idempotent, upsert, foreign key. Which are you comfortable with?

Never list a term that was not naked by the rules above. No naked terms, no footer.

When the user answers:

- **Comfortable.** Append the term to the glossary under the matching domain heading, or under the current project's heading if the term is project vocabulary, creating the heading if it doesn't exist. Write the base form: singular, uninflected, acronym and not expansion.
- **Not comfortable.** Run the clarify loop below.
- **No answer.** Add nothing. The term stays naked and gets glossed again next conversation.

## The clarify loop

When the user says a term didn't land, pause whatever was running and offer three ways forward:

Pick one:
1. Synonyms: "per-item lookups", "one query per row".
2. A new gloss, one level simpler or with an example.
3. I re-explain the paragraph that used it without the term.

Give two or three real synonyms in option 1, ones the user is likely to know. Repeat the loop until the user says they get the meaning, through the term itself or a synonym, or drops it.

Once they get it, the term goes in the glossary. If a synonym carried it, store the original term with the synonym in a parenthetical, `N+1 query ("one query per row")`. Keep using the original term, since docs and code use it. When the user later asks about the term, lead with their synonym.

Then resume exactly where the loop interrupted. If a question was pending, as in a grill session, ask it again word for word so the user does not have to scroll back.

## Seeding

When the user types `/gloss-me` with no task in progress, fill the glossary one domain at a time.

1. Ask which domain. "This project" is a valid answer, and its terms come from the project's `CONTEXT.md` and docs and go under its project heading.
2. List 30 to 50 common terms from it, numbered, skipping anything on the floor or already in the glossary. Pick the terms a working practitioner uses daily, not textbook trivia.
3. The user names the numbers they *don't* know. Those stay naked.
4. Append every other term under that domain's heading and offer the next batch or another domain.
