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

The ticket's Spec, plus every amendment note on the issue, applied in date order. Notes in the old look, first line `## Spec amendment`, count the same as notes in the current look. An amendment replaces the Spec line it quotes. Read the Spec this way wherever a station says "the ticket", never the body alone.

## Amendments

The ticket body never changes. When a Spec line has to:

1. Propose it to the user: the line as written, the change, and the reason. Wait.
2. On approval, post the same amendment note on the issue and on the ticket PR, then continue.
3. On refusal, the Spec line stands.

Fill in the template below.

- The `##` heading names the Spec line and the change in a few words.
- The short diff holds only the changed clause, a few words either side, with the change in git word-diff markers: `[-removed-]` and `{+added+}`.
- Under **Full lines**, the `-` row is the Spec line verbatim and the `+` row is the approved line verbatim. Under each row that has an unchanged part, a caret row marks the changed part with `^`, starting in the column where it starts. A caret row starts with two spaces, so it is never a `-` or `+` row.
- For an added line, both diffs hold only a `+` row with the whole line, and the heading ends `new line`. For a removed line, only a `-` row, and the heading ends `removed`. Neither gets a caret row.

````md
# Spec amendment

## <Spec line, like Behaviour 4>: <old words> → <new words>

```diff
! <changed clause, like: $max:grill-docs once{+ per session+}, and asks>
```

## Why

<one line>

## Date

<YYYY-MM-DD>

<details><summary>Full lines</summary>

```diff
- <the Spec line, verbatim>
  <spaces, then ^ under the changed part>
+ <the approved line, verbatim>
  <spaces, then ^ under the changed part>
```
</details>
````

The first line is always `# Spec amendment`, exactly. That is how a station finds one. Older notes start `## Spec amendment` and use `Date:`, `Original:`, `Change:` and `Reason:` lines. Read them too, and never post a new one in that look.

To read a note in the current look, take the old line from the `-` row and the new line from the `+` row under **Full lines**, minus the `- ` or `+ ` prefix. Skip caret rows. No `-` row means an added line, and no `+` row means a removed one.
