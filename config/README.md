# config

The skills in this repo are half of what makes Claude Code and Antigravity (agy) useful to me. This directory is the other half: the global instruction file, the settings that turn features off, the hooks that re-state a rule the model would otherwise drift from, and the status line.

**Nothing here is installed.** `install.sh` does not touch this directory and never will. There is exactly one `~/.claude/settings.json` and one `~/.gemini/config/` per machine, and overwriting yours with mine would eat whatever you already had. Read the files, take the parts you want, paste them into your own.

It is split per agent, and each folder is complete on its own, duplicated hook scripts included:

```
claude/   CLAUDE.md, settings.json, hooks/, statusline-command.sh
agy/      AGENTS.md, settings.json, hooks.json, hooks/
```

Install steps are in [`claude/README.md`](claude/README.md) and [`agy/README.md`](agy/README.md). The rest of this file is why the settings are what they are, which is the same for both.

---

## What all of this is for

A common issue with AI is that they **hallucinate** information and a big part of the problem is that you do not know what exists in an agents **context window**. That is the issue this part of my claude setup does: 

**Controlling what is in the context window at all times**.

The goal is to make an AI agent stateless and as predictable as possible. In order to achieve this I have done some settings to help. 

Predictable does not mean byte-identical, and chasing that would be silly. It means the same task takes the same route, stops at the same checkpoints, and lands the same artifacts. That level of repeatability is worth paying tokens for, which is the whole argument for enforcing rules with hooks rather than hoping the model remembers.

---

## CLAUDE.md

Two lines. That is the point.

```
- Push back on user input and ensure a mutual understanding before writing.
- Check all output, file or chat, against the unslop skill before sending. No em dashes.
```

A long global instruction file is a tax on every session, and the model follows the first half of it and forgets the rest. Anything longer than a couple of lines belongs in a skill I invoke when I need it, or in a project's own `CLAUDE.md`. These two earn their place because they apply to literally every turn.

The first line is the one I would keep if I could keep only one. Without it the default is to agree and start writing, and I get a confident implementation of the thing I asked for rather than the thing I meant. With it I get a question first. Most of `kanban/` and all of `grilling` build on the same instinct, so the global file and the skills push the same direction.

---

## What I turn off

Claude Code ships with more than I want loaded. Everything I disable is in one table. Each row is off because it puts something in the context window I did not choose, or lets the session act in a way I cannot reproduce.

| Off | Why |
|--------|-----|
| `autoMemoryEnabled` | Notes from unrelated sessions, loaded before I type. Context I did not pick, and it makes this run depend on the last one. |
| `disableBundledSkills` | The bundled skills' descriptions sit in context every turn whether they fire or not. Off, the only skills advertised are mine. |
| `disableWorkflows` | Lets a run land output somewhere other than the terminal and the repo. |
| `disableArtifact` | Same call. One landing place for work, and it is files under git. |
| `disableClaudeAiConnectors` | Connected services put a run's inputs outside the repo, where I cannot hold them still. |
| `disableRemoteControl` | No driving this session from elsewhere. |
| `EnterPlanMode`, `ExitPlanMode` | Plan mode overlaps with what my skills already do, and does it more vaguely. `architect-ticket` writes the plan as stubs and failing tests in real files, which is a better artifact than a plan I approve and then watch drift. |
| `AskUserQuestion` | Multiple-choice popups. `grilling` is one question at a time with a recommended answer and room to argue back, which is the interaction I actually want. |
| `NotebookEdit` | I do not work in notebooks. |
| `DesignSync` | Not part of how I work. |
| `SendMessage` | No subagent chatter. Skills in this repo hand off through artifacts, never by messaging each other, so nothing needs it. |
| `PushNotification`, `RemoteTrigger`, `ReportFindings` | Ways for a session to reach out beyond the terminal. Same call as the connector flags. |
| `ScheduleWakeup`, `CronCreate`, `CronDelete`, `CronList` | Scheduled runs. A session that fires while I am not watching is a session I cannot correct, and I would rather start every run myself. |

The last seven rows are the `permissions.deny` block, and they are denied for the same reason as the bundled skills. An available tool carries its description and its schema in context on every turn, and it can get reached for on turns where it does not belong. Denying the ones I never use keeps both out.

Two of these earn more than a table row.

`autoMemoryEnabled: false` is the one that matters most. Memory means every session opens with a pile of notes from sessions that were about something else. That is context spent before I have typed a word, on information I did not pick and whose size I cannot see, and it only grows. Give the same task to a fresh install and to mine and you get different work, and the difference lives in a file I never read. Since my preferences shift between projects and over months, a stale note does not just cost tokens, it steers wrong. Whatever is worth persisting goes in `CONTEXT.md` or an ADR, in a commit, scoped to one repo, where I can read it and challenge it.

`disableBundledSkills` is the same argument applied to the other end. Claude Code ships its own skills, and I have my own set, so their descriptions are a fixed tax for capability I am not using. Off, the model sees only mine, which is both cheaper and the reason the same prompt reaches for the same skill twice. It makes `/skills` readable too.

---

## unslop, and why it is wired in three times

`unslop` is the rule set in [`behaviour/unslop`](../behaviour/README.md). It strips the patterns that make text read as machine-written: em dashes, puffery, bold-label-plus-colon lists, "delve", "crucial", hedging, passive voice, chatbot filler. It matters to me more than any other skill in the repo, because I do not want a shorter time-to-first-draft. I want a draft I can send. Text that gives itself away in the first sentence fails that even when every fact in it is right.

The problem is that a rule read once at the start of a session loses to the model's defaults by turn twelve. Long output is where the tells come back, and long output happens late. That makes it a predictability problem before it is a writing problem, since the same request gets a clean answer early in a session and a sloppy one late in a long one. So the rule is enforced three ways at once, and the redundancy is deliberate.

**The skill.** `behaviour/unslop/SKILL.md` is the full rule set and the single source of truth. It is model-invoked, so it fires when Claude notices writing is happening, and any other skill can borrow it by name.

**`inject_unslop.py`**, a session-start hook. Prints that same `SKILL.md` into context at startup, resume, clear, and compact. Model invocation is a judgment call and it misses. This makes the rules present from turn one whether or not anything invoked them. It also survives a compact, which is exactly when a rule loaded early would otherwise fall out.

**`remind_unslop.py`**, a per-prompt hook. Prints a condensed version, about twelve lines of the highest-frequency offenders, immediately before every reply. This is the one that does the real work. Recency wins over a rule sitting thousands of tokens back, and the failure mode I am fixing is drift, not ignorance.

That is roughly 250 tokens on every turn, plus the full skill at session start. If you copy one piece, copy `remind_unslop.py`. If you copy nothing else from this directory, copy that.

Both hooks are unconditional and fire in sessions with no writing in them at all. I have decided that is worth it. You may not, and skipping the session-start injection while keeping the per-prompt reminder is a reasonable middle.

The event names and the output format differ per agent. Claude Code wires them to `SessionStart` and `UserPromptSubmit` and reads plain text on stdout. Antigravity has no session-start event, so both scripts run on `PreInvocation` and the inject script guards on the invocation counter. Each agent folder has its own copies of the scripts for that reason.

---

## statusline-command.sh (Claude Code only)

Model name, a context-usage bar, five-hour and weekly rate-limit usage, working directory, git branch.

![Status line showing model name, context usage bar, five-hour and weekly rate-limit usage, working directory, and git branch](img/statusline-example.png)

The context bar is capped at 150k tokens rather than the model's real window, deliberately. Quality falls off well before the window is full, and the bar going red is my cue to `/clear` and start the next step from the artifact the last one wrote. That is the same handoff the `kanban/` chain runs on, so the number is a workflow signal, not a memory gauge.

Needs `jq`. The reset-time formatting uses BSD `date -j`, so on Linux that line needs `date -d @"$epoch" "+%H:%M"` instead. Everything else is portable.
