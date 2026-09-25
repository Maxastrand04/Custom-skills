# ADR-0005: Support Antigravity alongside Claude Code

**Decision:** `install.sh` MUST be able to link skills into both Claude Code (`~/.claude/skills/<name>`) and Antigravity (`~/.gemini/config/skills/<name>`), by symlink, from the same skill directories. There is one install path; the repo MUST NOT carry a second discovery mechanism such as `.agents/skills.json`. Config under `config/` MUST be split per agent, `config/claude/` and `config/agy/`, each complete on its own even where files duplicate, and MUST stay reference-only.

**Reason:** Both agents read a `SKILL.md` with `name` and `description` frontmatter and discover skills by bare directory name, so one skill tree serves both without a build step, and the symlink keeps ADR-0002's live-edit property. A second discovery path for the same skills would mean two places to explain and two to get wrong. Config is split rather than shared because the two agents' hook contracts differ (plain text on stdout versus JSON with `injectSteps`, `SessionStart` versus `PreInvocation`) and a folder someone can copy whole is worth more than deduplicated scripts.

**Consequence:** Skills are shared exactly, config is not. A change to the unslop reminder text has to be made in both `config/claude/hooks/` and `config/agy/hooks/`.

Antigravity ignores `disable-model-invocation`, so ADR-0004's split between model-invoked and user-invoked skills holds there only by description wording. A skill outside `behaviour/` whose description reads as a trigger will be auto-invoked in Antigravity and not in Claude Code. ADR-0004 already requires descriptions written for a human reader; this is the second reason to keep it that way, and it is a known gap rather than a solved one.

Whether `~/.gemini/config/AGENTS.md` loads as a global rule is documented but untested. `config/agy/README.md` says so.

**Date:** 2026-09-22
