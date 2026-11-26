# Subagent prompt

The wrapper `tdd-ticket` puts above a station's `SKILL.md` text. Fill the placeholders, then send everything between the lines. `<station folder>` is the absolute path of `../<station>/`, resolved from `tdd-ticket`'s own directory.

---

You are running the `<station>` skill for ticket #<N> on branch `<branch>`, in the project at `<project root>`. Its full `SKILL.md` follows below this wrapper. Follow it as written, with the changes listed here. The skill's own folder is `<station folder>`, and every `../` path in it resolves from there, never from the project.

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

On a restart, append this after the station's text:

```
## Resume

A previous run of this skill halted. Continue from step <Step>. Don't redo the steps before it.
Commits it already made: <Commits from the halt block>
The halt: <Point>
The answer: <the orchestrator's or the user's answer>
```

Carry every earlier answer for this station too, one `The answer:` line per halt, oldest first.
