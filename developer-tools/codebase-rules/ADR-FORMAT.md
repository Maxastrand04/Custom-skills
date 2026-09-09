# ADR format

The single source of truth for every ADR this system writes. Every skill that touches `docs/adr/` reads this file rather than restating it.

ADRs live in `docs/adr/` as `NNNN-slug.md`, numbered sequentially. Create the directory lazily, when the first ADR is written.

**An ADR is a decision that binds.** There is no second, softer kind. A recorded choice about the shape the codebase takes *is* a rule, so write it as one and let a reviewer cite it by number. Anything too soft to bind is not an ADR; leave it out rather than filing a preference nobody can enforce.

## Template

```md
# ADR-NNNN: {imperative title, for example "Handlers depend inward"}

**Decision:** {one imperative sentence, phrased as MUST or MUST NOT}. For example: "Code in `handlers/` MUST NOT import from `infra/`; depend on `core/` interfaces instead."

**Reason:** {why this was chosen, and what was chosen against}. Name the alternative that was weighed and why it lost.

**Consequence:** {what this forces on the codebase from here on}. What a future change has to live with, and what breaks if someone works around it.

**Date:** {YYYY-MM-DD}
```

Four fields, every one required.

- **Decision** is what a reviewer cites. Imperative, one sentence, one thing.
- **Reason** is what stops a future reader undoing it by accident. An ADR that only records *what* was decided is half an ADR: the reader sees the shape, sees no argument for it, and "simplifies" it away. Name the road not taken.
- **Consequence** is what makes the decision checkable without a check recipe. A reader who knows what the decision forces can tell compliance from breach in a diff, and a consequence stays true when the tooling changes.
- **Date** is when the decision last changed, not when it was first written. `challenge-adr` bumps it on every amendment.

## Optional lines

Add only when they earn their place:

- **Scope:** the paths, layers, or contexts the decision covers, when it isn't the whole repo.
- **Exceptions:** narrow, named carve-outs. A decision riddled with exceptions is really two decisions, or none.
- **Status:** `retired`, set by `challenge-adr` when the code the decision governed no longer exists. Retired ADRs stay on disk so old review comments and branches still resolve the number. Absent means live.

## One decision per file

Never bundle two. The value is that `ADR-0012` names exactly one thing, so "violates ADR-0012" is unambiguous and the reader loads one short file. A candidate with an "and" in it is two ADRs.

The filename slug is the decision's shorthand. Pick it so `docs/adr/` reads as an index at a glance: `0012-no-orm-in-domain.md`, not `0012-database.md`.

## Who writes, who changes

**Writing a new ADR** is open to any skill that shapes the codebase. Take the next free number, scanning `docs/adr/` for the highest in use.

**Changing or retiring an existing ADR takes a full `/challenge-adr` session, and there is no other route.** No skill edits a file in `docs/adr/` in passing, not to fix drift, not to reword, not to retire, and no skill deletes one. These numbers are cited in review comments, commits, and open branches, so a decision that shifts meaning under them costs more than it looks like it costs.

Reading `challenge-adr` and applying its reasoning inline is **not** a substitute for running it. The session exists because an ADR only moves once a challenge has been argued against it and won, and that argument needs the user in the room.

So when an ADR blocks the work in front of you:

1. **Stop at the ADR.** Name it, and name what it blocks, in one line.
2. **Hand it to the user** to run `/challenge-adr`. You do not run it for them, and you do not run it as part of the current session.
3. **Assume it stands.** Until that session returns a verdict, the decision binds. Never write code, or an interface, on the assumption that the challenge will succeed.
