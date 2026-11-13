# kanban-ci

The back half of the kanban board, run by GitHub Actions instead of by me. I architect a ticket by hand, queue it, and the loop runs `implement-ticket`, `refactor-ticket` and `unit-test-ticket` overnight with nobody watching. In the morning there is a PR, and `review-ticket` walks me through it.

`kanban/` stays the proven, interactive version. Nothing in here edits it, and nothing in `kanban/` knows this folder exists. `install.sh` doesn't install it either. It ships as a plugin.

## How a ticket moves

1. `/architect-ticket` commits and pushes the red branch once you approve it, and opens the draft **ticket PR**, the one PR the branch keeps from start to merge. The contract is `skills/pr-ticket/ticket-pr.md`, copied from kanban.
2. `/kanban-ci:launch` adds `Handoff-To: implement-ticket` in an empty commit on top, since the architect commit is already pushed, pushes, and labels the issue `ci:queued`.
3. The nightly run, or `gh workflow run kanban-ci --ref <branch>`, starts the loop in `scripts/run-chain.sh`. It reuses the open ticket PR, or opens a draft on a branch architected before there was one. A branch whose PR merged or closed is skipped.
4. The loop runs whichever station `HEAD`'s `Handoff-To` trailer names. After each one it pushes, posts the comment the station wrote on the ticket PR, runs the whole suite once, and passes the result to the next station in its prompt. Stations never touch GitHub themselves.
5. Stations hand off forward, back a station, or early to `review`. Two backward moves per ticket at most. A third ends the chain.
6. The loop rewrites the ticket PR's description. On a finished chain, `pr-ticket` first writes the body's Summary, Evidence, Merge danger and For the reviewer sections from the commits, with Merge danger flagging changes callers may rely on and changed behaviour no test protects, and the loop marks the PR ready. A halted chain skips `pr-ticket`, stays a draft with a plain body listing every station's `For the reviewer` items, and gets a comment naming the halt.
7. `/kanban-ci:review-ticket <PR>` on my laptop goes through those items with me, applies the fixes I approve, and writes a comment on the ticket PR. My own test workflow checks the PR, and I merge.

Commit bodies are written for the next agent. Station comments on the ticket PR are the same progress notes kanban's stations post. The review session's comment is the one written for a human. The issue gets only the `Ticket PR:` link and Spec amendments, and only the review session proposes amendments, since headless stations have no one to approve them.

## Setup, once per machine

```
claude plugin marketplace add Maxastrand04/Custom-skills#release
claude plugin install kanban-ci@custom-skills
```

That gives `/kanban-ci:launch` and `/kanban-ci:review-ticket` on the laptop. `#release` reads the `release` branch, which only moves when a new version goes out. If you added the marketplace earlier without it, re-add it once:

```
claude plugin marketplace remove custom-skills
claude plugin marketplace add Maxastrand04/Custom-skills#release
claude plugin install kanban-ci@custom-skills
```

The shared workflow and template below still track `main`. The runner loads the plugin straight from a checkout of this repo, so it needs no install.

## Setup, once per project

1. **Token.** Run `claude setup-token` and save the output as the repo secret `CLAUDE_CODE_OAUTH_TOKEN`. Runs then use the Claude subscription, not API billing, and they count against the same usage limits as my laptop sessions.
2. **Let Actions open PRs.** Settings, Actions, General, tick "Allow GitHub Actions to create and approve pull requests".
3. **Caller workflow.** Copy `templates/kanban-ci.yml` to `.github/workflows/kanban-ci.yml` on the default branch, and fill in the three `SET-ME` values. The scheduling rules are below.
4. **A test workflow of the project's own**, running on `pull_request`. That is the merge gate. kanban-ci doesn't replace it.
5. **Optional, `KANBAN_CI_PUSH_TOKEN`.** GitHub doesn't trigger workflows on pushes or PRs made with the default Actions token. Without this secret, the test workflow won't run on the loop's PR until the review session pushes. A fine-grained personal access token with Contents, Pull requests and Issues write on the repo fixes that.

## Scheduling

**Pick the hour on purpose.** Every repo with kanban-ci draws from the same Claude usage window, and GitHub can't queue runs across repos. Two repos scheduled at the same hour split one window between them, and both stall.

- Give each repo its own `cron` hour, a few hours apart. Cron times are UTC.
- Keep a list of which repo has which hour. It isn't stored anywhere else.
- The template ships with `cron: "SET-ME"`, which GitHub rejects. The workflow can't run, manual runs included, until a real time is chosen.

When a run hits the usage limit, the ticket stays queued and no PR opens. The next run picks up from the newest commit's `Handoff-To`, and work the station hadn't committed is lost.

## Models and limits

`refactor-ticket` runs on Opus, `implement-ticket`, `unit-test-ticket` and `pr-ticket` on Sonnet, which suits the Pro plan. Turn limits per station and the 330-minute job timeout are inputs on the reusable workflow, `.github/workflows/kanban-ci.yml`, for tuning after the first real runs.

Permission prompts are skipped on the runner. It's a throwaway machine, and the job's GitHub permissions limit it to this repo's code, PRs and issues.

## Keeping in step with kanban

The four station skills are full forks of their `kanban/` originals, rewritten to run with nobody to ask. Each records its source as a line at the top, `synced-from kanban/<skill>/SKILL.md blob <hash>`.

```
ci/scripts/sync-from-kanban.sh                         # copy rule files, show skill drift
ci/scripts/sync-from-kanban.sh --mark refactor-ticket  # after porting by hand
```

The rule files, `code-standards.md`, `test-standards.md`, `RECORD-FORMAT.md`, `pr-shape.md` and `ticket-pr.md`, are copied byte for byte. Where a rule file asks the user something, as `ticket-pr.md` does about a closed PR, the loop or the headless station's `SKILL.md` says what happens instead. For skills it prints what changed in kanban since the fork, and porting is a choice made by hand. Changes only flow from kanban to ci, never back.
