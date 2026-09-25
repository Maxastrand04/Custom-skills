# config/agy

Everything Antigravity (agy) reads from `~/.gemini/config/`, its global customization root. Why each piece exists lives in [`../README.md`](../README.md).

```
AGENTS.md               global rules
settings.json           tool deny list and disabled autoMemory
hooks.json              wires both scripts to PreInvocation
hooks/inject_unslop.py  first invocation: prints the full unslop skill into context
hooks/remind_unslop.py  every invocation: twelve-line reminder before the model runs
```

## Install

Nothing here is installed by `install.sh`. Copy by hand.

```bash
mkdir -p ~/.gemini/config/hooks
cp config/agy/AGENTS.md ~/.gemini/config/AGENTS.md    # or merge into yours
cp config/agy/hooks.json ~/.gemini/config/hooks.json  # or merge the two entries into yours
cp config/agy/hooks/*.py ~/.gemini/config/hooks/
chmod +x ~/.gemini/config/hooks/*.py

# Merge settings into ~/.gemini/antigravity-cli/settings.json:
# permissions.deny: ["ask_question", "generate_image"]
# autoMemory: false
```

`inject_unslop.py` reads `~/.gemini/config/skills/unslop/SKILL.md`, so install the `unslop` skill with `./install.sh --agy` first or the hook injects nothing.

## What differs from Claude Code

Antigravity hooks take JSON on stdin and return JSON on stdout. A `PreInvocation` hook returns `{"injectSteps": [{"ephemeralMessage": "..."}]}` and the message lands as a transient system message before the model runs. There is no session-start event, so `inject_unslop.py` runs on `PreInvocation` and only emits when `invocationNum` is 1. The docs do not say whether that counter resets per user turn or per conversation, so on a long conversation the full skill may be injected more than once. That costs tokens, nothing else.

`AGENTS.md` at `~/.gemini/config/` is the documented global location, but I have not confirmed it loads. If rules seem absent, put `AGENTS.md` at the workspace root instead, which is the discovery path the docs describe in most detail.

Antigravity ignores `disable-model-invocation` in skill frontmatter. Every skill you install is offered to the model by its description, so the user-invoked split from [ADR 0004](../../docs/adr/0004-skills-are-user-invoked-outside-behaviour.md) holds only as far as the descriptions read as summaries rather than triggers.

The CLI settings file lives at `~/.gemini/antigravity-cli/settings.json`. `config/agy/settings.json` contains the `permissions.deny` block (`ask_question`, `generate_image`) and `autoMemory: false` to ensure runs remain stateless.
