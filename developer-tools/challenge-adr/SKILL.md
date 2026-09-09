---
name: challenge-adr
description: Test whether a recorded ADR still stands, and amend or retire it only if the challenge wins.
disable-model-invocation: true
---

# challenge-adr

**An ADR stands until a challenge beats it.** You are not here to update a document, you are here to find out whether a decision someone weighed still holds, and most of the time it does.

This is the only way an ADR in `docs/adr/` changes or retires, and it takes a whole session to do it. Read [`../codebase-rules/ADR-FORMAT.md`](../codebase-rules/ADR-FORMAT.md) before writing anything.

**The burden is on the challenge, and it is heavy.** A decision was recorded because someone weighed alternatives. "This is inconvenient", "the current code doesn't do this", and "I'd have chosen differently" are not arguments, they are the friction the ADR was written to create. Overturning one takes a case that the codebase gets architecturally better on a named axis: looser coupling, tighter cohesion, stronger encapsulation, a dependency pointing the right way, easier testing. Anything else and the ADR stands.

---

## 1. Pin the challenge

Settle two things before reading any code:

- **Which ADR.** By number, or by describing the decision. Resolve it in `docs/adr/` and read the file in full.
- **What the user wants**, in one sentence, and **why**. If the invocation came from another skill hitting a blocker, the challenge is whatever that skill wanted to do and couldn't.

If the challenge is really "I don't want to follow this right now", say so plainly and stop. That's an answer, and it takes one line.

## 2. Investigate

Read, don't ask, for anything the code can answer:

- **The code the decision governs.** Does it comply today? Drifted code is a finding either way, and it changes what the challenge means.
- **Neighbouring ADRs.** A decision rarely stands alone. If ADR-0012 exists because ADR-0007 set a dependency direction, overturning it reaches further than one file.
- **What the Reason field names.** The alternative that lost. Ask what changed since: did the trade-off actually shift, or does the user just not know the argument?

Emit a short **"What I found"**: whether the code complies, which ADRs are entangled, and whether the original trade-off still applies. Wait for the user to correct misreads.

## 3. Judge

Weigh the challenge against the recorded decision, out loud, and lead with your own verdict. Three outcomes:

**Stands.** The default, and the most common. The Reason still holds, or the challenge is convenience rather than architecture. Say which and stop. Nothing is written.

- If the **code** has drifted from a decision that stands, the code is what's wrong. Report the breach and hand it to the user or to `refactor-ticket`. Never amend an ADR to match code that wandered off.

**Amend.** The decision's shape changes, and the codebase is better for it on one of the named axes above. Grill the user into the new Decision, Reason, and Consequence before touching the file. Then edit in place:

- **Keep the number.** Review comments, commits, and open branches cite it.
- **Rewrite Decision, Reason, and Consequence together.** A Reason left describing the old trade-off is worse than no Reason.
- **Record what was overturned** in the new Reason. The next reader needs to know this ground was fought over once.
- **Bump the Date** to today.

**Retire.** The code the decision governed no longer exists, so there is nothing left to bind. Set `**Status:** retired`, bump the Date, and leave the file on disk. Never delete an ADR.

Retire is for a decision with no subject left. A decision that is now *wrong* is an amendment, not a retirement.

**Completion criterion:** a stated verdict with its reasoning, and for an amendment or retirement, the file edited and the Date bumped.

## 4. Report

Three lines, nothing after:

```
ADR-0012  no-orm-in-domain
Verdict   amended, scope narrowed to src/domain/
Ripple    ADR-0007 unaffected, 3 files now breach, handed to refactor-ticket
```

If the verdict is **stands**, the Ripple line names what the user has to do instead.
