---
name: grill-docs
description: Beside the board, for any session that should keep the docs right. Grills a plan, change, or idea against CONTEXT.md and the project's records, and writes terms, ADRs, and new PCRs as they settle. Works with a ticket or without one.
disable-model-invocation: true
---

# grill-docs

Grill the user about whatever they bring, and keep the project's docs in step with what the grill settles. Those are the two fixed parts. Everything else is the user's call: a ticket or no ticket, a plan or a half-formed idea, whether they write code in this session afterwards, whether they commit. Never steer them into the ticket chain or a TDD flow.

The docs are `CONTEXT.md` and the records in `docs/adr/` and `docs/pcr/`. Their shapes are fixed:

- `CONTEXT.md` follows [`CONTEXT-FORMAT.md`](CONTEXT-FORMAT.md), beside this file.
- Every ADR and PCR follows [`../architect-ticket/RECORD-FORMAT.md`](../architect-ticket/RECORD-FORMAT.md). Read it before writing or amending a record. Its tests decide what earns a record, and its writer rules decide what this skill may touch.

---

## 1. Explore before asking

Read, where present:

1. `CONTEXT.md` at the root, or `CONTEXT-MAP.md` and the context files it points to.
2. Every file in `docs/pcr/` and `docs/adr/`.
3. The top-level `README.md` and the root listing.
4. A ticket, if the user named one. Resolve it with `gh issue view <ref> --json title,body,labels` and treat its body as input to the grill, not as a contract to enforce.
5. The code the topic touches. Grep for it and read the modules and their neighbours.

Then post a short **"What I found"**: the terms that apply, the records that bind this area, and anything in the code that already disagrees with them. Wait for the user to correct misreads.

## 2. Grill

Run the session under the `grilling` skill's interview mechanics, so invoke it. Alongside its rounds, do four things whenever they come up:

- **Challenge against the glossary.** When the user uses a term in a way that conflicts with `CONTEXT.md`, say so in that round: "CONTEXT.md defines **Order** as X, but you seem to mean Y. Which is it?"
- **Sharpen fuzzy words.** When a term is vague or carries two meanings, propose one canonical term and the ones to avoid.
- **Test with scenarios.** Invent a concrete case that probes the edge between two concepts, and make the user say which side it falls on.
- **Check claims against the code.** When the user says how something works, read the code. A mismatch is a question for the next round, never a silent correction.

Check the plan against the records too:

- **A plan that breaks an ADR** is a question. Either the plan changes or the ADR does. If the user argues the ADR should change and names a reason the record didn't anticipate, amend it in step 3.
- **A plan that breaks a PCR** stops at the PCR. Name it and what it blocks, in one line. Point the user at `/challenge-pcr` and don't run it for them. Until that session returns a verdict, the PCR stands, so carry on with the rest of the grill on that assumption.

The grill ends where `grilling` says it does, when every branch is visited and the user confirms you understand each other.

## 3. Write the docs as they settle

Write each change when its decision settles, not in a batch at the end. A change written mid-grill is visible to the user in the next round and cheap to correct there.

**`CONTEXT.md`.** When a term is resolved, add or revise its entry, its Relationships lines, and the example dialogue if the term changes how it reads. Create the file when the first term resolves, never before. It stays a glossary. Implementation details, plans, and decisions never go in it.

**ADRs.** A decision the grill argued against a named alternative is a candidate. Run it through the record format's tests and the spine test. Write one that passes, taking the next free number, and drop the rest without comment. Most grills settle most things without argument, and those produce nothing. Amend an ADR the same way the format describes: keep the number, rewrite Decision, Reason, and Consequence together, bump the Date. Retire one whose code is gone. The reason for an amendment goes to the user in the session and nowhere in the file.

**PCRs.** Write a new one when this session is the first to settle something project-wide, such as the first test runner or naming style in a repo with no `docs/pcr/` entry for it. Never edit, reword, retire, or delete an existing PCR. That takes `/challenge-pcr`.

Create `docs/adr/` or `docs/pcr/` only when the first record lands in it. Write without asking, then say what changed in one line in the next round, for example `Docs  CONTEXT.md: Invoice added. ADR-0004 written.`

## 4. After the grill

Report every doc change from the session in one block:

```
CONTEXT.md   Invoice added, Order revised
Records      ADR-0004 written, ADR-0002 amended
```

Write `none` on a line with no changes. An amended ADR also gets one line with its reason, `ADR-0002 amended: <why, one line>`, so the user can put it in their commit message, since the file carries no history.

Then hand control back. Don't commit, open a ticket, or suggest a next skill unless the user asks. If the user keeps working in this session and something new settles, such as a renamed term or an argued decision, update the docs the same way.
