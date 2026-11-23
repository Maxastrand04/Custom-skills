---
name: amend-pcr
description: Weigh a proposed change to a project convention record (PCR) in docs/pcr/ and amend or retire it only once the user approves. Use when a PCR blocks the current work, or when the user wants to change or retire a project convention.
---

# amend-pcr

**A PCR stands until a case beats it, and only the user can say it was beaten.** Your job is to lay out what an amendment costs and give an honest verdict. The decision is never yours.

**You never edit a file in `docs/pcr/` without the user's approval of the exact change in this session.** Not to unblock yourself, not to fix a typo, not because the verdict looks obvious. Step 5 is the only place a PCR file changes, and you reach it only through step 4.

You want the block gone, which makes you the worst judge of whether it should go. So the burden sits on the amendment, and it is heavy. "This is inconvenient", "the current code doesn't do this" and "I'd have chosen differently" are not reasons. They are the friction the PCR was written to create.

Read [`../grill-docs/RECORD-FORMAT.md`](../grill-docs/RECORD-FORMAT.md) before writing anything. ADRs are out of scope here.

---

## 1. Pin the amendment

- **Which PCR.** Resolve it in `docs/pcr/` and read the whole file.
- **What should change, and why**, one sentence each. When a blocked session loaded this skill, the change is whatever it wanted to do and couldn't.

If the real request is "I don't want to follow this right now", say so in one line, give the verdict **stands**, and go back to the work.

## 2. Measure the ripple

The ripple is everything the amendment would touch. Read the code for it, don't ask:

- Grep the project for what the convention governs and count the files.
- Check whether the code follows the PCR today. Drift is a finding either way.
- List the ADRs that lean on this PCR and would need amending too.
- Read the Reason field. It names the alternative that lost. Ask what changed since.

Rank every item in the ripple:

| Rank | Meaning | Example |
|------|---------|---------|
| High | The amendment breaks existing code, which then has to change to comply | Changing the naming convention renames identifiers in every file |
| Medium | Existing code still complies, but new code may be written a different way | Allowing a second HTTP library beside the current one |
| Low | It adds an option and nothing existing is affected | Allowing a test helper library nobody uses yet |

## 3. Make the case

Present it in this order, in one message:

1. **What approval takes.** The case has to show the whole project gets better and that the ripple is worth paying. Name what would have to be true for that here.
2. **The ripple**, as the ranked table from step 2, highest first, with the file count and the entangled ADRs.
3. **Reasons not to amend.** Always first, and never empty. The Reason field is the starting point.
4. **Reasons to amend.**
5. **Verdict and recommendation.** One of:
   - **Stands.** The default and the most common. The Reason still holds, or the case is convenience. If the code has drifted from a PCR that stands, the code is wrong. Never amend a PCR to match code that wandered off.
   - **Amend.** The case beats the Reason field and the ripple is worth paying.
   - **Retire.** The thing the PCR governs no longer exists in the project. A PCR that is now wrong is an amendment, not a retirement.

## 4. Ask the user

For an amend or retire verdict, list the proposed changes to the file before asking:

```
PCR-0002  no-orm
Decision     <new sentence>
Reason       <new reason, naming what lost>
Consequence  <new consequence>
Date         <today>
```

For a retirement, the list is `Status: retired` and the Date.

Then ask the user to approve, change, or reject. Stop and wait. Silence, a question, or "sounds reasonable" is not approval. If they change the wording, show the list again and ask again.

When the verdict is **stands**, still ask. The user may overrule you, and then you draft the change list with them in this step.

## 5. Write, only after approval

- **Amend.** Edit in place. Keep the number, since commits and reviews cite it. Rewrite Decision, Reason and Consequence together, so no field describes the old trade-off. Bump the Date.
- **Retire.** Set `**Status:** retired` and bump the Date. Never delete a PCR.
- **Rejected.** Write nothing. The PCR stands.

The reason for the change goes to the user in one line for the commit message, never into the file. Don't stage or commit.

## 6. Report and hand back

Three lines:

```
PCR-0002  no-orm
Verdict   amended, ORM allowed in reporting/ only
Ripple    41 files (12 high), ADR-0009 needs amending
```

Name the code that no longer complies and the ADRs that need amending, but fix neither. The user decides where that work goes.

Then return to the session that loaded this skill. An amended PCR binds from here on, so the work continues under the new wording. A PCR that stands sends the session back to what it does when blocked.
