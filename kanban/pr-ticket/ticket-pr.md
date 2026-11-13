# Ticket PR

Shared contract. Every ticket branch has one **ticket PR**, a draft pull request opened when the branch is created and kept through review. The ticket holds the spec. The ticket PR holds everything that happens to the branch after that: progress, review notes, findings, handoffs. `pr-ticket`, or `execute-ticket` on its own route, rewrites its description and marks it ready at the end.

## Open or reuse it

Every station runs this once the branch is checked out and before it changes anything else. A station that creates the branch runs it straight after `git checkout -b`.

```
gh pr list --head <branch> --state all --json number,state,url
```

- **An open PR.** That is the ticket PR. Reuse it.
- **A merged PR, none open.** Halt: `The PR for <branch> merged as #<PR>. More work needs a new ticket and branch.`
- **A closed PR, none open or merged.** Ask the user whether to reopen it with `gh pr reopen <PR>` or start fresh with a new draft below. Wait for the answer.
- **No PR.** Open one:

  1. If `git rev-list --count <base>..HEAD` is `0`, GitHub refuses a PR, so make an empty start commit: `git commit --allow-empty -m "Start #<N>: <ticket title>" -m "Issue: #<N>"`.
  2. `git push -u origin <branch>`.
  3. `gh pr create --draft --base <base> --title "<ticket title>" --body-file <file>`, with the body below, written to a temp file outside the repo.
  4. Link the ticket back: `gh issue comment <N> --body "Ticket PR: <PR URL>"`.

```md
> *Draft. Development history for this ticket collects in the comments below. The description is rewritten when the branch is ready.*

Closes #<N>
```

If any of these commands fails, halt with its error and change nothing more. No station develops on a branch without a ticket PR.

**Completion criterion:** the PR number of one open ticket PR, and the issue carries a `Ticket PR:` comment linking it.

## Where notes go

Post every progress note, review note, finding, `For the reviewer` item and handoff on the ticket PR with `gh pr comment <PR> --body-file <file>`. The issue gets only the `Ticket PR:` link and amendment notes.

Branches started before this contract keep their earlier notes on the issue. When reading history, read both: `gh issue view <N> --comments` and `gh pr view <PR> --comments`.

## Current Spec

The ticket's Spec, plus every amendment note on the issue, applied in the order they were posted. Notes in any older look, first line `###### Spec amendment`, `# Spec amendment` or `## Spec amendment`, count the same as notes in the current look. Read the Spec this way wherever a station says "the ticket", never the body alone.

## Amendments

The ticket body never changes. When a Spec line has to:

1. Propose it to the user: the line as written, the change, and the reason. Wait.
2. On approval, post the same amendment note on the issue and on the ticket PR, then continue.
3. On refusal, the Spec line stands.

Fill in the template below.

- The second line names the section, `Interface`, `Behaviour` or `Out of scope`, and the change, `added`, `removed` or `rewritten`.
- `Why:` is one sentence.
- The diff's first line is the position, `@@ <section> <n> @@`. `n` counts the lines of that section in the current Spec from 1, top to bottom, so Behaviour's edge-case bullets carry on from its last numbered step. For an added line, `n` is where the new line goes.
- The `-` row is the Spec line verbatim and the `+` row is the approved line verbatim. An added line has only a `+` row, and a removed line only a `-` row.
- Nothing else goes outside the fold.

````md
##### Spec amendment

<section>: <added, removed or rewritten>

Why: <one sentence>

<details><summary>Details</summary>

```diff
@@ <section> <n> @@
- <the Spec line, verbatim>
+ <the approved line, verbatim>
```
</details>
````

The first line is always `##### Spec amendment`, exactly. That is how a station finds one.

To read a note in the current look, take the section and `n` from the `@@` line, the old line from the `-` row, and the new line from the `+` row, each minus its `- ` or `+ ` prefix. Then:

- **Both rows.** Replace line `n` of that section with the new line.
- **Only a `-` row.** Remove line `n`.
- **Only a `+` row.** Insert the new line at position `n`, moving the line there and every one after it down by one.

A note whose first line is `###### Spec amendment` has the same shape. Read it the same way, and never post a new one with that heading.

Older notes start `# Spec amendment` or `## Spec amendment`. Neither carries a position, so find the line they change by its text: the `-` row under **Full lines** in the first, the `Original:` line in the second. Skip caret rows, which start with two spaces. An added line in either look has no old line, so put it at the end of the section its heading or `Change:` line names. Read both looks, and never post a new note in either.
