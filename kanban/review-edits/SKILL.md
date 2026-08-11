---
name: review-edits
description: Review the committed diff before it's pushed along two parallel axes — Standards (conforms to the rule-ADRs in `docs/adr/`, plus code smells) and Spec (faithful to the originating issue's acceptance criteria, no scope creep). Handles both a full `implementation-plan-execute` run and a small issue done inline with no plan. Use when the user finishes work, says "review-edits", "review the edits", "review this branch", or "run the code-review session".
---

# review-edits

The reviewer at the end of the work — run when changes are ready to push. It judges the committed diff against how this repo says code must be written and against what the originating issue asked for. Two kinds of work reach it:

- **Plan-backed** — a full `implementation-plan-execute` run. Verification already ran every `AC-N` test green, so **does-it-work is settled**; you judge **is-it-right**.
- **Issue-only** — a small issue done inline, no plan and no Verification. Nothing gated the acceptance criteria, so here you also check the diff actually meets them.

Two axes, run as **parallel sub-agents** so they don't pollute each other's context:

- **Standards** — does the diff conform to how this repo says code must be written: the rule-ADRs in `docs/adr/`, plus the code-smell baseline below.
- **Spec** — does the diff faithfully implement the originating acceptance criteria, and nothing they didn't ask for.

## 1. Pin the work and the diff

Find the source of truth for this change — a plan, or an issue:

**Plan-backed** — `plan N.N` in the invocation, or a plan file in `implementation_plans/` matches the work. Read from it — **point at the file, don't paste it back into your context**: `**Branch:**`, `## Rules in play`, `## Acceptance criteria`. Verification already ran the ACs green.

**Issue-only** — no plan. The branch under review carries its **GitHub issue number** in the name (the branch-naming convention every issue publishes). Take the current branch (or the one the user names), extract the issue number, and fetch it: `gh issue view <number>` — its acceptance criteria are the contract, and **no Verification ran**. Two guards:

- If the branch name carries no issue number, the convention was skipped — ask the user which issue this closes, and flag that the branch should be renamed to include the number.
- If the issue doesn't already record which branch implements it, backfill the link: `gh issue comment <number>` with a one-line `Reviewed on branch \`<branch>\``.

Then, both ways: the diff under review is `git diff main...HEAD` (three-dot, against the merge-base) on that branch; substitute the base the user names if not `main`. Confirm the branch resolves and the diff is non-empty before spawning sub-agents — a bad ref or empty diff fails here, not inside a sub-agent. Capture the commit list too: `git log main..HEAD --oneline`.

## 2. Standards sources

Two tiers, both handed to the Standards sub-agent:

1. **Rule-ADRs in `docs/adr/`** — the enforceable rules (`**Rule:** … **How to check:** …`). A breach is a **hard violation** — cite `ADR-NNNN` and its `How to check` line. Which ADRs apply depends on the flow:
   - **Plan-backed** — the ADRs named in the plan's `## Rules in play` bind this change **directly**; the rest of `docs/adr/` still governs.
   - **Issue-only** — no `## Rules in play` pre-selected them, so the sub-agent takes the **whole `docs/adr/` set** and judges which rule-ADRs the changed files fall under itself.
   - Either way, if the diff itself modifies files under `docs/adr/` (a rule added or amended during the work), flag it for the user.
   - If `docs/adr/` doesn't exist yet, the axis runs on the smell baseline alone — note it in the report.
2. **Code-smell baseline** — always applies, even where no ADR covers the code: bad code is still flagged. Each smell is a **judgement call** ("possible Feature Envy"), never a hard violation, and **any rule-ADR overrides it**. Skip anything a linter/typechecker/compiler already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

## 3. Spec source

The acceptance criteria are the contract:

- **Plan-backed** — the plan's `## Acceptance criteria`. Verification already ran these green — **do not re-run them**; the axis is a read for faithfulness and scope.
- **Issue-only** — the acceptance criteria in the fetched issue. **No Verification ran**, so the axis must check the diff actually satisfies each one — not assume it.

## 4. Spawn both sub-agents in parallel

One message, two `Agent` calls, `general-purpose` for both.

**Standards sub-agent** — include: the diff and commit-list commands; the rule-ADRs to check against (plan-backed: the paths in `docs/adr/`, flagging which are named in `## Rules in play`; issue-only: the whole `docs/adr/` directory for the agent to judge relevance itself); and the code-smell baseline from step 2 pasted in full — the sub-agent has no other access to it. Brief: *"Report per file/hunk: (a) every hard violation of a rule-ADR that applies to the changed files — cite ADR-NNNN and its How-to-check line; (b) every baseline smell — name it and quote the hunk; (c) any modification the diff makes to files under `docs/adr/`. Hard violations are ADR breaches; smells are always judgement calls, and a rule-ADR overrides a smell. Skip anything a linter/typechecker/compiler enforces. Under 400 words."*

**Spec sub-agent** — include: the diff and commit-list commands, and the acceptance criteria (plan-backed: the path to the plan file, to read `## Acceptance criteria` from directly; issue-only: the fetched issue text). Brief depends on the flow:

- **Plan-backed:** *"The AC tests already pass — do NOT re-run them. Report: (a) acceptance criteria the diff implements incompletely or wrongly despite a green test (e.g. a weak test, or a `(manual)` AC); (b) behaviour in the diff that no AC asked for (scope creep). Quote the AC line for each finding. Under 400 words."*
- **Issue-only:** *"No tests were gated for this change. Read the diff against each acceptance criterion and report: (a) any criterion the diff leaves unmet or only partially met; (b) behaviour in the diff that no criterion asked for (scope creep). Quote the criterion for each finding. Under 400 words."*

If there are no acceptance criteria to check against (no plan and no issue), skip the Spec sub-agent and say so.

## 5. Aggregate

Present the two reports under `## Standards` and `## Spec`, verbatim or lightly cleaned. Do **not** merge or rerank across axes — they're deliberately separate. End with one line per axis: finding count and the worst issue within that axis.

The output is a report to the user, who decides what to act on — you don't post it or fix anything (the issue-link backfill in step 1 is the only write). Real findings typically feed a fresh `implementation-planning` cycle or a direct fix.

## Why two axes

Verification (or, for issue-only work, this session) settles does-it-work; you settle is-it-right, and the two halves of "right" fail independently:

- Follows every rule-ADR but drifts from the acceptance criteria → **Standards pass, Spec fail.**
- Matches the acceptance criteria exactly but breaks a rule-ADR → **Spec pass, Standards fail.**

Reporting them separately stops one from masking the other.
