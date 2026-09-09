# ADR-0004: Skills are user-invoked outside `behaviour/`

**Decision:** Every Skill outside `behaviour/` MUST set `disable-model-invocation: true` in its frontmatter, and its `description` MUST be written for a human reader rather than as invocation triggers. Only a Skill in `behaviour/` may be model-invoked.

**Reason:** The alternative was model-invoking everything, which buys two things: Claude can fire a Skill on its own, and one Skill can reach another by name. Both lost. Autonomous firing hands Claude the decision about what work happens next, which is the decision most worth keeping, and every model-facing description sits in the context window on every turn whether or not it is used. Twenty-two of them is real load for Skills that mostly open a session. A `behaviour/` Skill is different in kind. It is borrowed by work already running rather than starting any, so `grilling`, `unslop`, and the two Talk-to Skills have to be reachable from inside another Skill, and their descriptions earn what they cost.

**Consequence:** Cross-Skill invocation is no longer available outside `behaviour/`, so every handoff has to run through an artifact. The `kanban/` chain passes an epic issue, a ticket, and a red branch; `brainstorming` ends by naming a route instead of taking it; a Skill blocked by an ADR stops and names it rather than opening `challenge-adr`. A new Skill that needs another Skill's logic reads a bundled file or gets restructured, and never gets a reach clause added to its description.

The load moves rather than disappearing. Eighteen Skills now have nothing in the window to remind me they exist, and remembering them is mine. When that outgrows memory, the fix is a router Skill that names the others, not relaxing this decision.

In a diff, a breach looks like a `SKILL.md` outside `behaviour/` with no `disable-model-invocation` line, a description carrying trigger phrasing such as "Use when the user says", or a Skill instructing Claude to invoke a non-`behaviour/` Skill by name.

**Date:** 2026-09-02
