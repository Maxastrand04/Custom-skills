# Subagent prompt

The prompt `tdd-ticket` sends to a station's subagent. Fill the placeholders, then send everything between the lines. Never append the station's `SKILL.md`.

---

Invoke the `<station>` skill through the Skill tool for ticket #<N> on branch `<branch>`, in the project at `<project root>`. Use its installed name, including its plugin prefix when present. Follow the skill with the changes listed here and any Option or Resume block in this prompt. Resolve the skill's relative paths from the skill directory supplied by the tool, never from the project.

If the skill is unavailable, return a halt block with Point `skill unavailable`. Never read its `SKILL.md` as a fallback.

A user started an orchestrator session, and you report to it. The user is not reading this conversation.

- **Never ask and never wait.** Wherever the skill asks the user something, waits for an answer or approval, or offers the user options, stop there and return a halt block instead. Do what the skill says about posting the halt on the ticket PR first.
- **Never load `amend-pcr`, and never amend an ADR or PCR.** When the skill would, halt instead.
- **Skip the skill's closing line that names the next skill**, such as `Next, run /pr-ticket`.

End your final message with exactly this block, and nothing after it:

```
Station   <station>
Result    green | halt
Step      <the step you finished or stopped at, by its heading>
Commits   <short hash and subject of every commit you made, or none>
Point     <the question you need answered, one line, or none>
Evidence  <what you saw, one or two lines, or none>
Guess     <your best guess at the cause, stated as a guess, or none>
Options   <the options the skill names for this stop, or none>
```

`green` means the skill reached its report with nothing left to ask.

---

## Resume block

On a restart, append this to the subagent prompt. Apply it when invoking the skill:

```
## Resume

A previous run of this skill halted. Continue from step <Step>. Don't redo the steps before it.
Commits it already made: <Commits from the halt block>
The halt: <Point>
The answer: <the orchestrator's or the user's answer>
```

Carry every earlier answer for this station too, one `The answer:` line per halt, oldest first.
