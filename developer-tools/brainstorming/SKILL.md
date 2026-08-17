---
name: brainstorming
description: Grill an idea until it either dies or holds, then route the surviving idea to the skill that should build it.
disable-model-invocation: true
---

# brainstorming

An idea has arrived. The product of this skill is a **shaped** idea — one that has already been through the gaps that would otherwise surface as refactors later. The instrument for shaping it is trying to **kill** it: hunt for where the idea falls apart, then either adapt it to survive that or conclude it can't be.

A first idea is almost never what gets built. Treating one as sound because the user likes it is the failure this skill exists to prevent, so the grill argues against the user by default and looks for the break, not the confirmation.

Size is not a factor. A one-line refactor and a brand-new product run the same loop; they differ only in how long they take to exhaust and where they route at the end.

## 1. Grill to kill

Run `/grilling` on the idea. That skill owns the interview mechanics — one question at a time, recommended answer first, explore the codebase instead of asking whenever the codebase holds the answer.

Two things this grill does that a plain grill does not:

- **Argue its death.** At least once, make the strongest honest case for not doing this at all — do nothing, buy it instead, delete the code rather than extend it, live with the problem. Press the case; do not raise it and move on. An idea never asked to die only ever gets confirmed.
- **Reshape on every break.** A gap that surfaces is not a strike against the idea, it is the work: adapt the idea to close it and keep grilling the adapted version. Most of a run is this loop, and the shaped idea it produces is the deliverable.

There is no fixed set of angles. The idea decides what gets attacked — follow whatever the last answer exposed, and go where the idea is weakest rather than where it is easiest to discuss.

Completion: **exhausted** — you cannot produce a question whose answer would change the verdict. Not a topic count, and not the point where the user sounds convinced.

## 2. Verdict

Binary. State it outright, in the user's face, before anything else.

- **Killed** — one line for what killed it, plus what would have to become true to revive it. No route. Stop here.
- **Holds** — one paragraph of concrete functionality: what it does, what changes observably, and what it deliberately does not cover. This is the surviving idea, not the one that walked in.

No hedged third outcome. If it half-holds, the half that holds is the idea and the rest is out of scope — say so in the paragraph.

## 3. Propose what to document

The grill usually settles something worth keeping. Propose it — never write silently:

- A rule that constrains future work → an ADR in `docs/adr/`, per `../codebase-rules/RULE-ADR-FORMAT.md` (read it at runtime).
- A term the grill pinned down or renamed → an entry in `CONTEXT.md`.

Propose nothing when the grill settled nothing durable; a killed idea can still be worth an ADR recording why not.

Write only on approval.

## 4. Route

Only if it holds. Name one route and state the reason, so the user can override it:

| The surviving idea is… | Route |
|---|---|
| One change, one test suite, no architecture question | `/implement-tdd` |
| One coherent behaviour needing a spec, no epic covering it | `/new-issue` |
| Big enough to need phases, Groups, and acceptance criteria | `/implementation-planning` |
| A goal that has to be sliced into several tickets | `/epic-planning` |
| A whole new product, or a repo with no `CONTEXT.md` / `project_plan.md` yet | `/project-planning` |

Route to the smallest thing that fits. Ceremony an idea does not need is a cost, not a safety net — "this is one file and one test, no plan earns its keep here" is a complete justification.

Hand off; do not start building. The routed skill runs its own grill on the surviving idea.
