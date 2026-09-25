# config/claude

Everything Claude Code reads from `~/.claude/`. Why each setting is what it is lives in [`../README.md`](../README.md).

```
CLAUDE.md               global instructions, two lines
settings.json           feature toggles, permissions.deny, hooks, statusLine
hooks/inject_unslop.py  SessionStart: prints the full unslop skill into context
hooks/remind_unslop.py  UserPromptSubmit: twelve-line reminder before every reply
statusline-command.sh   model, context bar, rate limits, cwd, branch
```

## Install

Nothing here is installed by `install.sh`. Copy by hand.

Copy `settings.json` wholesale only if your `~/.claude/settings.json` is empty. Otherwise merge key by key. The hooks and the status line are separate files and go into `~/.claude/` as they are:

```bash
mkdir -p ~/.claude/hooks
cp config/claude/hooks/*.py ~/.claude/hooks/
cp config/claude/statusline-command.sh ~/.claude/
chmod +x ~/.claude/hooks/*.py ~/.claude/statusline-command.sh
cp config/claude/CLAUDE.md ~/.claude/CLAUDE.md   # or merge into yours
```

Then add the matching `hooks` and `statusLine` blocks from `settings.json`. Both use `$HOME` rather than a hardcoded path, so they work on any account.

`inject_unslop.py` reads `~/.claude/skills/unslop/SKILL.md`, so install the `unslop` skill first or the hook prints nothing.

The status line needs `jq`. The reset-time formatting uses BSD `date -j`, so on Linux that line needs `date -d @"$epoch" "+%H:%M"` instead.
