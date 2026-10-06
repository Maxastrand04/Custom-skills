# kanban-ci

The back half of the kanban board, run by GitHub Actions instead of by me. I architect a ticket by hand, queue it, and the loop runs `implement-ticket`, `refactor-ticket` and `unit-test-ticket` overnight with nobody watching. In the morning there is a PR, and `review-ticket` walks me through it.

`kanban/` stays the proven, interactive version. Nothing in here edits it, and nothing in `kanban/` knows this folder exists. `install.sh` doesn't install it either. It ships as a plugin.

## How a ticket moves

1. `/architect-ticket` commits the red branch, the same as always.
2. `/kanban-ci:launch` adds `Handoff-To: implement-ticket` to that commit, pushes, and labels the issue `ci:queued`.
3. The nightly run, or `gh workflow run kanban-ci --ref <branch>`, starts the loop in `scripts/run-chain.sh`.
4. The loop runs whichever station `HEAD`'s `Handoff-To` trailer names. After each one it pushes, runs the whole suite once, and passes the result to the next station in its prompt.
5. Stations hand off forward, back a station, or early to `review`. Two backward moves per ticket at most. A third ends the chain.
6. The loop opens a PR that closes the issue on merge. On a finished chain, `pr-ticket` first writes the body's Summary, Evidence and Merge danger sections from the commits. A halted chain skips it and gets a draft with a plain body. Every station's `For the reviewer` items are collected into the PR body either way.
7. `/kanban-ci:review-ticket <PR>` on my laptop goes through those items with me, applies the fixes I approve, and writes the issue comment. My own test workflow checks the PR, and I merge.

Commit bodies are written for the next agent. The issue comment is written for a human, and only the review session writes it.

## Setup, once per machine

```
claude plugin marketplace add Maxastrand04/Custom-skills
claude plugin install kanban-ci@custom-skills
```

That gives `/kanban-ci:launch` and `/kanban-ci:review-ticket` on the laptop. The runner loads the plugin straight from a checkout of this repo, so it needs no install.

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

The rule files, `code-standards.md`, `test-standards.md`, `RECORD-FORMAT.md` and `pr-shape.md`, are copied byte for byte. For skills it prints what changed in kanban since the fork, and porting is a choice made by hand. Changes only flow from kanban to ci, never back.
