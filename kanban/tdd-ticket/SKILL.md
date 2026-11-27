---
name: tdd-ticket
description: Runs a medium, major or minor ticket's whole route from one session. You settle the design once, then review the PR. Takes the ticket reference as its argument. Claude Code only.
disable-model-invocation: true
---

# tdd-ticket

You are the **orchestrator** for one ticket. The user settles the design with you once, and next sees the PR. Every station after the architect runs in a fresh subagent, and you stand between those subagents and the user: you answer what you may, and escalate what you may not.

The stations are model-invoked. Start `architect-ticket` and `pr-ticket` through the Skill tool in this chat. For every other station, start a fresh subagent that invokes the station through its own Skill tool. Never read or copy a station's `SKILL.md` into this session or a subagent prompt. If the skill is unavailable, report a halt instead of copying its instructions. See ADR-0001 and ADR-0004.

Every `../` path resolves from this skill's directory. Never search the repo for it.

---

## 1. Pin the work

Resolve the ticket from the invocation argument, meaning `42`, `#42`, or a GitHub issue URL. No argument means ask which issue, and stop until told.

`gh issue view <N> --json title,body,labels,state,comments`. Read the current Spec per `../helper-skill/ticket-pr.md`.

Stop with one line, and do nothing else, when any of these holds:

- **Trivial.** `This ticket is labelled trivial because no test covers it. Run a supervised session instead.`
- **Unlabelled.** No `effort:` label: `#<N> has no effort label. Label it per ticket-shapes.md and start again.`
- **Question ticket.** It has a Question and no Spec: `#<N> is a question ticket. Nothing to implement.`
- **Merged.** The branch's ticket PR merged: `The PR for <branch> merged as #<PR>. More work needs a new ticket and branch.`

**Branch.** `<N>-<slug>`, per the ticket's `## Branch` section, or the current branch when the user named it or it already carries the number. Base is the repo's default branch unless the user names one.

**Rerun guard.** If the branch exists and carries commits beyond its `Start #<N>` commit, stop. Name the last leg reached from the newest commit subject it carries, then stop:

| Subject | Last leg |
|---|---|
| `Architect #<N>` | red, by `architect-ticket` |
| `Implement #<N>` | green, by `implement-ticket` |
| `Refactor:` or `Fix #<N>` | refactor, by `refactor-ticket` or `review-diff` |
| `Tests #<N>: tidy and fold` | unit tests, by `unit-test-ticket` |
| `Test #<N>` | red, by `execute-ticket` |

> #<N>'s branch already reached <leg>. tdd-ticket doesn't resume an interrupted run.

Then route on the label: `medium` or `major` to step 2, `minor` to step 4.

## 2. Architect with the user (medium, major)

Invoke `architect-ticket` through the Skill tool with the ticket reference, in this chat, with the user, on this session's model. It borrows `grill-docs` for the grill. Stop at its step 6 Confirm: skip the line pointing at `/implement-ticket`, since you start it next.

Keep what the grill settled in mind. It is the context you answer later halts from.

## 3. Run the later legs (medium, major)

Run each station in a fresh subagent, in this order, per **Starting a subagent** below:

| Station | Model |
|---|---|
| `implement-ticket` | haiku, then sonnet per **Haiku halts** |
| `refactor-ticket` | opus |
| `unit-test-ticket` | sonnet |

Each must return `Result  green` before the next starts. Then go to step 5.

## 4. Run the minor route

| Station | Model |
|---|---|
| `execute-ticket` | sonnet |
| `review-diff` | opus |

Start `execute-ticket` with the line `Option: orchestrated` in its prompt, before it invokes the skill. Then `review-diff`. Then go to step 5.

**Mislabelled.** When `execute-ticket` halts on its qualifying check, or on a record or decision halt, the ticket is not `minor`. Stop the route. Post one comment on the ticket PR with `gh pr comment <PR> --body-file <file>`:

```md
**Not minor.** <the check that failed, one line>. The real level is `effort:<level>`, because <why, one line>.
```

Name no skill in it. Tell the user the same in chat and stop.

## 5. PR and report

Start `pr-ticket` through the Skill tool with the issue number. If it halts, pass the halt on word for word and stop.

Then post in chat, and nowhere else:

```
PR        <URL>
Decisions
- <station> step <n>: <the halt, one line> -> <your answer, one line>
- implement-ticket halted on haiku at step <n>: <point>, retried on sonnet
```

List every decision you made without the user, and every haiku halt. Write `Decisions none` when there were none. Then every line of `pr-ticket`'s report from `Title` on.

---

## Starting a subagent

Use the Agent tool with `subagent_type: general-purpose` and the station's model. Build the prompt from the wrapper in `subagent-prompt.md`, beside this file, with its placeholders filled. Include `Option: orchestrated` for `execute-ticket`.

On a restart, append the resume block from that file, carrying every earlier answer for this station. The subagent invokes the station through its own Skill tool and applies the wrapper and resume instructions to that invocation. Use the skill name exposed by the installed catalog, including its plugin prefix when present.

Wait for it to finish. Read its last block, the halt block the wrapper defines. Anything else, such as a missing block, counts as a halt with the point `no result block`.

## Halts

For each halt, decide in this order. The first rule that matches wins.

1. **Same point twice.** The station already halted on this point once in this run, on whatever model. Escalate.
2. **Spec, public interface, ADR or PCR.** The answer would change the Spec, a settled entry point, an ADR, or a PCR. Escalate, on every level. Never load `amend-pcr` or edit a record yourself.
3. **A test the ticket didn't add.** The answer deletes a test that was on the base branch. Escalate.
4. **Major.** The ticket is `effort:major` and the grill didn't settle the point. Escalate.
5. **Otherwise** answer it yourself, from the grill's context, the ticket, and the code. You may settle implementation details. You may change or delete an acceptance test that still follows the Spec and the public interface after the change. Note the decision for step 5's report.

Then restart the same station in a fresh subagent with the answer, per **Starting a subagent**. Never restart from the top. The resume block tells it which step to continue from. See ADR-0014.

### Haiku halts

When `implement-ticket` halts on haiku, apply the rules above. If you answer the halt, restart it on sonnet, and keep it on sonnet for the rest of this ticket's `implement-ticket`. Other stations keep their own model. Report every haiku halt in step 5, so the user can judge whether sonnet should be the default.

### Escalation

Ask the user in this chat. Never post an escalation as a PR comment, and never send the user to a new session. Give the station, the step, the point, the evidence, and the options from the halt block, plus your recommendation. Wait. Then restart the station with the user's answer, or stop if the user says stop.
