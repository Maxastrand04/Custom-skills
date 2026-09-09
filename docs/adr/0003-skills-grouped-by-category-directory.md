# ADR-0003: Skills are grouped by category directory, but install flat

**Decision:** Every Skill MUST live one level down under a category directory, and `install.sh` MUST still symlink it to a flat `~/.claude/skills/<name>`. The categories are `kanban/` for the workflow chain, `developer-tools/` for everything else for coding, `behaviour/` for wording and interaction rules borrowed by Skills in any other category, `schoolwork/` for study skills, and `archive/` for retired Skills, which are never installed.

**Reason:** We rejected a flat repo because the top level had grown to fifteen sibling directories with no signal about which ones form the workflow and which are standalone. We rejected encoding the category in the Skill name, as in `kanban-project-planning`, because the name is what you type and `/project-planning` should stay short, and because moving a Skill between categories would then rename it. The install stays flat because Claude Code discovers Skills by bare directory name and does not read nested categories.

**Consequence:** The category is repo-level metadata only, so Skill names must stay unique across categories. Adding a category means adding it to the `CATEGORIES` array in `install.sh`. Moving a Skill between categories leaves a stale symlink, which `install.sh` silently re-points when the old target is inside this repo.

**Date:** 2026-08-22
