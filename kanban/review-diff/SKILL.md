---
name: review-diff
description: Clean up the committed diff before it's pushed — first gate it true-to-spec (the acceptance tests genuinely test the acceptance criteria), then edit the code into line with the rule-ADRs in `docs/adr/` and the code-smell baseline, and report what was found and how it was fixed. Use when the user finishes work, says "review-diff", "review the diff", "clean up this branch", or "run the code-review session".
---

# review-diff

The last station on the board — run when changes are ready to push. The implementer is given wide freedom in *how* the code gets written, so this session is **cleanup**: you don't just judge the diff, you fix it.

Two passes, in order, and the first gates the second:

1. **True-to-spec** — the acceptance tests genuinely test the acceptance criteria, and the code satisfies them. Read-only.
2. **Cleanup** — edit the code into line with the rule-ADRs in `docs/adr/` and the code-smell baseline.

Cleaning code that's wrong spec-wise is wasted work — pass 1 exists to prove only cleaning is left.

## 1. Pin the work and the diff

Find the source of truth for this change — a plan, or an issue:

**Plan-backed** — `plan N.N` in the invocation, or a plan file in `implementation_plans/` matches the work. Read `**Branch:**`, `## Public interface` and `## Acceptance criteria` from it; each `AC-N` names its test in a `Verify:` line, and Verification already ran them green.

**Issue-only** — no plan. The branch under review carries its **GitHub issue number** in the name (the branch-naming convention every issue publishes). Take the current branch (or the one the user names), extract the number, and fetch it: `gh issue view <number>` — its acceptance criteria are the contract, and **no Verification ran**, so nothing is known-green yet.

- If the branch name carries no issue number, the convention was skipped — ask the user which issue this closes, and flag that the branch should be renamed to include the number.
- If the issue doesn't already record which branch implements it, backfill the link: `gh issue comment <number>` with a one-line ``Reviewed on branch `<branch>` ``.

Then, both ways: the diff under review is `git diff main...HEAD` (three-dot, against the merge-base) on that branch; substitute the base the user names if not `main`. Confirm the branch resolves and the diff is non-empty before going further. Capture the commit list too: `git log main..HEAD --oneline`.

## 2. Pass one — true-to-spec

**Make no edits in this pass.** Work through the acceptance criteria one at a time:

- **Is the test true to the criterion?** Read the test named in the AC's `Verify:` line (plan-backed) or the test that claims to cover it (issue-only). A test that asserts something weaker than the criterion, stubs out the behaviour it should exercise, or passes vacuously is **not** true to spec, green or not.
- **Does the diff meet the criterion?** For `(manual)` criteria and anything no test covers, read the code against the AC directly.
- **Did anything arrive that no criterion asked for?** Scope creep is a spec finding too.

Plan-backed: **don't re-run the AC tests here**, you're reading for faithfulness. Issue-only: nothing gated them, so run them.

**Completion criterion:** every acceptance criterion accounted for — each one either true-to-spec or a named finding.

Zero findings → the spec is settled, go to pass 2. Any finding → **halt**.

### The spec halt

Stop and report the findings — quote the criterion and the test or hunk for each. Then ask the user whether to fix the acceptance **tests** so they're true to their criteria. Only the tests: the AC text itself is the plan's or issue's single source of truth and is never edited here.

With their go-ahead, fix the tests and run them:

- **Still green** — the implementation was right and the test was merely thin. Continue to pass 2.
- **Now red** — the weak test was hiding a real gap. **Stop here.** Closing that gap is implementation work, not cleanup: hand the failing tests back to a fresh implementer and wait. Don't implement it yourself.

## 3. Pass two — cleanup

Edit the code directly — this pass produces changes, not a list of suggestions.

Two tiers:

1. **Rule-ADRs in `docs/adr/`** — the enforceable rules (`**Rule:** … **How to check:** …`). A breach is a **hard violation**: fix it, and cite `ADR-NNNN` in the report. No plan pre-selects rules, so take the **whole `docs/adr/` set** and judge yourself which rules the changed files fall under.
   - If the diff itself modifies files under `docs/adr/` (a rule added or amended during the work), flag it for the user rather than acting on it.
   - If `docs/adr/` doesn't exist, this pass runs on the smell baseline alone — note that in the report.
2. **Code-smell baseline** — always applies, even where no ADR covers the code. Each smell is a **judgement call**, and **any rule-ADR overrides it**. Skip anything a linter, typechecker, or compiler already enforces.

Two standing exemptions:

- **Tests are exempt from the smell baseline.** A test that is true to its AC stays as written — duplication, long setup and all. Only a rule-ADR that explicitly governs tests touches them.
- **Cleanup never changes behaviour.** If a fix would alter what the code does, it isn't cleanup — leave the code alone and report it as a finding for the user.

The baseline, *what it is* → *how to fix*:

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

**Completion criterion:** every changed non-test file has been read against the whole `docs/adr/` set and the full baseline above, and each hit is either fixed or recorded as a deliberate non-fix with a reason.

## 4. Re-run and commit

The AC tests are the safety net under the refactor. Run every one of them:

- **All green** — commit the cleanup as its own commit on the branch, so the implementer's work and the cleanup stay separately readable. Subject: `Cleanup: <plan title or issue title>`. Don't push unless the user asks.
- **Any red** — the break is yours, not the implementer's. Fix or revert the cleanup edit that caused it, then re-run. Never amend a test to accommodate a cleanup edit.

## 5. Report what changed

One short line per change, in the shape *what you found* → *how you fixed it*:

```
src/pricing.ts — duplicated code — extracted `applyDiscount` helper, both call sites now use it
src/order.ts — ADR-0004 (no direct DB calls in handlers) — moved the query into `OrderRepository`
```

Then, only if non-empty:

- **Found, not fixed** — one line each with the reason (behaviour change, needs a decision, ADR file modified by the diff).
- **Spec fixes** — any acceptance test you repaired in pass 1, with the user's go-ahead noted.

Close with the change count and the commit sha. No essay — the list is the report.
