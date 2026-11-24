---
name: grill-docs
description: Grill the user relentlessly about a plan, decision, or idea, and write CONTEXT.md terms, ADRs, and new PCRs as they settle. Use when the user wants to stress-test their thinking, uses any 'grill' trigger phrases, or another skill needs interview mechanics.
---

# grill-docs

Interview the user relentlessly until you reach a shared understanding, and keep the project's docs in step with what the grill settles. Those are the two fixed parts.

A grill is **started** when the user asks for it directly, and **borrowed** when another skill invokes this one for its interview. Both run the same grill and write the same docs. A started grill leaves everything else to the user: a ticket or no ticket, whether they write code afterwards, whether they commit. Never steer them into the ticket chain or a TDD flow. A borrowed grill hands control back to the skill that invoked it, which decides what the grill is about and what happens after.

The docs are `CONTEXT.md` and the records in `docs/adr/` and `docs/pcr/`. Their shapes are fixed:

- `CONTEXT.md` follows [`CONTEXT-FORMAT.md`](CONTEXT-FORMAT.md), beside this file.
- Every ADR and PCR follows [`RECORD-FORMAT.md`](RECORD-FORMAT.md), beside this file. Its tests decide what earns a record, and its writer rules decide what this skill may touch.

---

## 1. Read first

Before the first round, read what this session hasn't read yet:

1. `RECORD-FORMAT.md`, beside this file.
2. `CONTEXT.md` at the root, or `CONTEXT-MAP.md` and the context files it points to.
3. Every file in `docs/pcr/` and `docs/adr/`.
4. A ticket, if the user named one. Resolve it with `gh issue view <ref> --json title,body,labels` and treat its body as input to the grill, not as a contract to enforce.
5. The code the topic touches. Grep for it and read the modules and their neighbours.

Don't summarise the reading back. Start the grill.

## 2. Grill

Map the topic as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

Alongside the rounds, do four things whenever they come up:

- **Challenge against the glossary.** When the user uses a term in a way that conflicts with `CONTEXT.md`, say so in that round: "CONTEXT.md defines **Order** as X, but you seem to mean Y. Which is it?"
- **Sharpen fuzzy words.** When a term is vague or carries two meanings, propose one canonical term and the ones to avoid.
- **Test with scenarios.** Invent a concrete case that probes the edge between two concepts, and make the user say which side it falls on.
- **Check claims against the code.** When the user says how something works, read the code. A mismatch is a question for the next round, never a silent correction.

Check the plan against the records too:

- **A plan that breaks an ADR** is a question. Either the plan changes or the ADR does. If the user argues the ADR should change and names a reason the record didn't anticipate, amend it in step 3.
- **A plan that breaks a PCR** stops at the PCR. Name it and what it blocks, in one line. Load `amend-pcr` for it. Until the user approves an amendment there, the PCR stands, so carry on with the rest of the grill on that assumption.

The grill is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## 3. Write the docs as they settle

Write each change when its decision settles, not in a batch at the end. A change written mid-grill is visible to the user in the next round and cheap to correct there. This holds for a borrowed grill too: whatever passes the tests gets written, whichever skill invoked this one.

**`CONTEXT.md`.** When a term is resolved, add or revise its entry, its Relationships lines, and the example dialogue if the term changes how it reads. Create the file when the first term resolves, never before. It stays a glossary. Implementation details, plans, and decisions never go in it.

**ADRs.** A decision the grill argued against a named alternative is a candidate. Run it through the record format's tests and the spine test. Write one that passes, taking the next free number, and drop the rest without comment. Most grills settle most things without argument, and those produce nothing. Amend an ADR the same way the format describes: keep the number, rewrite Decision, Reason, and Consequence together, bump the Date. Retire one whose code is gone. The reason for an amendment goes to the user in the session and nowhere in the file.

**PCRs.** Write a new one when this session is the first to settle something project-wide, such as the first test runner or naming style in a repo with no `docs/pcr/` entry for it. Never edit, reword, retire, or delete an existing PCR. That takes `amend-pcr` and the user's approval.

Create `docs/adr/` or `docs/pcr/` only when the first record lands in it. Write without asking, then say what changed in one line in the next round, for example `Docs  CONTEXT.md: Invoice added. ADR-0004 written.` Never stage or commit. A borrowed grill leaves that to the skill that invoked it, and a started grill leaves it to the user.

## 4. After a started grill

A borrowed grill skips this step and returns to the skill that invoked it.

Report every doc change from the session in one block:

```
CONTEXT.md   Invoice added, Order revised
Records      ADR-0004 written, ADR-0002 amended
```

Write `none` on a line with no changes. An amended ADR also gets one line with its reason, `ADR-0002 amended: <why, one line>`, so the user can put it in their commit message, since the file carries no history.

Then hand control back. Don't commit, open a ticket, or suggest a next skill unless the user asks. If the user keeps working in this session and something new settles, such as a renamed term or an argued decision, update the docs the same way.
