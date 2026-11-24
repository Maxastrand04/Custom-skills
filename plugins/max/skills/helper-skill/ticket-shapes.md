# Ticket shapes

The single source of truth for every ticket this system publishes, whether `new-ticket` files it standalone or `map-epic` files it under an epic. Body shape, title, labels, effort level, branch slug, the AI disclaimer, gh preflight, the publish loop, and native wiring all live here. Neither skill restates them.

## The two shapes

Every ticket is one of two bodies, and nothing else.

- **Task ticket**, `template_task_ticket.md`. Goal, Spec, Out of scope, Branch. Used for a deliverable: a standalone `feat` or `fix`, or an epic task.

  **Goal** is one sentence saying what the ticket delivers.

  **Spec** is how the developer pictures the solution working, written like pseudocode: concrete enough to follow through the code, with nothing named. One claim per line, no prose. It has two parts:

  - **Interface** lists the pieces the change adds or alters and what each one carries, in plain words. "A reusable button component" belongs here. `Button(color, width)` does not. Whoever implements the ticket turns these lines into the real names and signatures. They never become tests.
  - **Behaviour** is the happy path as numbered steps, read like a sequence diagram in text: who acts, on what, and what happens next. Edge cases and failure modes follow as unnumbered bullets. Every Behaviour line is covered by at least one test, except on an `effort:trivial` ticket, where the user checks the lines no test reaches.

  Spec never names a function, class, file, type, or test. Naming is HOW, and the implementation session settles it with the code open.

  **Out of scope** is a bullet list.
- **Question ticket**, `template_question_ticket.md`. A Question and nothing more. Used for research and prototype tickets, which exist to be answered in their own session, not implemented.

Read the template file at publish time. Do not reconstruct either body from this document.

## Title format

`<type>: <id> <short title>`, where the id is present only on epics and epic tasks.

- **Type** is lowercase and ends in a colon: `feat:`, `fix:`, `research:`, `prototype:`, `epic:`. It follows Conventional Commits, so a task ticket's title is already its PR title, and `pr-shape.md` copies it over.
- **Id** is `(N)` on an epic and `(N.M)` on an epic task, both assigned by `map-epic`. Standalone tickets, research tickets, and prototype tickets carry no id, since nothing is implemented from them and the GitHub issue number identifies them.
- **70 characters total**, counting type and id.
- Sub-issues of a standalone parent inherit the parent's type.
- No `parent:` marker. Parentage is visible through GitHub's native sub-issue list.

`feat: (3.2) Add OAuth login`, `fix: Expire sessions after idle timeout`, `research: Which payment provider supports SEPA`, `epic: (4) Self-serve billing`.

## Labels

Every ticket carries a `<scope>:<type>` label. Scope records where the ticket came from, and type records what kind of work it is.

| | task | research | prototype |
|---|---|---|---|
| **filed under an epic** | `epic:task` | `epic:research` | `epic:prototype` |
| **filed standalone** | `ticket:task` | `ticket:research` | `ticket:prototype` |

`feat` and `fix` both label as `task`. The title's type carries that distinction.

Every task ticket also carries one `effort:<level>` label, saying how much of the user the ticket needs. Question tickets carry none, since nothing is implemented from them. Decide the level with the effort criteria below, once per task ticket, at publish time.

Labels must exist before use, so create the ones this session needs, idempotently, once:

```
gh label create epic:task --color 1D76DB || true
gh label create epic:research --color 5319E7 || true
gh label create epic:prototype --color 0E8A16 || true
gh label create ticket:task --color 1D76DB || true
gh label create ticket:research --color 5319E7 || true
gh label create ticket:prototype --color 0E8A16 || true
gh label create effort:trivial --color C2E0C6 || true
gh label create effort:minor --color FBCA04 || true
gh label create effort:medium --color F9A03F || true
gh label create effort:major --color D93F0B || true
```

## Effort criteria

Effort measures how much of the user the ticket needs, not how big the diff is. A one-line change to a name half the codebase calls needs the user at every step, because getting it wrong breaks those callers. A large swap behind a stable interface needs only a review, because the tests decide whether it's right.

A module here is one file. A public interface is any name, parameter, or return value that code outside its own file calls or could call.

**Major checks.** The ticket is `major` if any of these hold:

1. **It needs a new module.** The work adds a file rather than changing existing ones.
2. **It changes the behaviour of more than one module.** Callers that only follow a renamed or reshaped interface don't count.
3. **It changes a public interface that more than one other module already calls.** An interface with no callers yet, or one caller, can still change cheaply. One the system depends on breaks in many places when it's wrong.
4. **`git revert` of the merged PR can't undo it completely.** A migration, an external resource, or data written that a revert leaves behind.

**Everything else** stays inside one module and reverts cleanly. Pick the first level that matches:

| Level | When | The user's part |
|---|---|---|
| `effort:major` | Any major check holds | Takes part in every step, from settling the interface to reviewing the code |
| `effort:medium` | The ticket changes a public interface, or needs an ADR or PCR in `docs/adr/` or `docs/pcr/` | Settles the interface, tests, and any record, then reviews the finished change |
| `effort:trivial` | Implementation only, a few lines, and a Behaviour line no automated test can reach | Works alongside the agent, keeps it inside the ticket, and checks what no test reaches |
| `effort:minor` | Implementation only, and automated tests reach every Behaviour line | Reviews the finished change |

Implementation only means no public interface changes and no record is needed.

A ticket with an untestable Behaviour line that is more than a few lines of work fits no level. Split the untestable part into its own `trivial` ticket.

Small refactors, bug fixes, and implementation swaps behind a stable interface are usually `minor`. The level is a guess made before anyone read the code, so whoever implements a `minor` ticket should re-check it and stop if it was wrong.

## Branch slug

**The ticket names its own branch.** Fill `## Branch` on every task ticket before its first preview. A ticket without one gets a slug guessed from its title, so filling it here keeps the slug deliberate. Question tickets have no branch, since nothing is implemented from them.

- **2 to 4 words, kebab-case, no articles**, derived from the title. `feat: Add OAuth login for admin dashboard` gives `oauth-admin-login`.
- **Slug only.** No issue number, since the issue does not exist yet and whoever opens the branch prepends it. No `feature/` prefix, no type prefix.

## AI disclaimer

Every published body starts with:

```
> *This was generated by AI during a ticket grill session.*
```

Both templates already carry it. Do not strip it, or the task template's Branch sentence, during inline edits.

## gh preflight

Before any grilling or publishing, confirm `gh` is installed, authenticated, and pointed at a real repo. Run, in order:

1. `gh --version`
2. `gh auth status`
3. `gh repo view`

Remediation:

- **`gh --version` fails.** `gh` is not installed. On macOS, run `brew install gh`. On other platforms, see https://cli.github.com/. Stop and wait for the user to install it.
- **`gh auth status` fails.** Tell the user to run `gh auth login`, and wait for them to confirm before proceeding.
- **`gh repo view` fails.** Ask the user which repo to file against, capture `owner/name`, and pass `--repo owner/name` to every later `gh` call this session.

Do not proceed until preflight passes or the `--repo` fallback is captured.

## Publish loop

Every ticket goes through the same loop: **preview, edit, approve, publish.**

1. **Preview the rendered title and body** as the chat message, showing the full title including id and type prefix, and the full body markdown. The user sees it before any `gh` call. A fenced code block is fine if it reads better.
2. **Accept natural-language inline edits**, such as "reword Behaviour step 3 as X", "drop the Out of scope bullet about Y", or "tighten the goal". Apply, re-render title and body in full, and offer the next cycle.
3. **Publish only on explicit approval.** Never assume it, and never publish silently.

```
gh issue create --title "<title>" --body "$(cat ...rendered...)" --label "<scope>:<type>" --label "effort:<level>"
```

Drop the effort label on a question ticket.

Capture the issue number and URL from the output. Every wiring call needs the **numeric database id**, not the number:

```
gh api repos/{owner}/{repo}/issues/<issue-number> --jq .id
```

## Native wiring

Parentage and blocking are **GitHub-native, never body text**.

Attach a ticket to its parent, whether that parent is an epic map issue or a standalone parent issue:

```
gh api repos/{owner}/{repo}/issues/<parent-issue-number>/sub_issues -X POST -F sub_issue_id=<child-numeric-id>
```

For each confirmed blocking edge, `X blocked by Y`:

```
gh api repos/{owner}/{repo}/issues/<X-issue-number>/dependencies/blocked_by -X POST -F issue_id=<Y-numeric-id>
```

Publish in **dependency order**, so a blocking edge always points at an issue that already exists. Start with tickets that have no blockers, and publish a ticket only once everything it is blocked by exists. A cycle in the graph means the split is wrong, so re-slice until it is acyclic.

Surface the parent URL and every child URL to the user once the wiring calls are done.
