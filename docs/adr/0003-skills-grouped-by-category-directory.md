# Skills are grouped by category directory, but install flat

Skills live one level down, under a category directory: `kanban/` for the workflow chain, `developer-tools/` for everything else for coding, `behaviour/` for wording and interaction rules, borrowed by Skills in any other category, `schoolwork/` for study skills, and `archive/` for retired Skills, never installed. `install.sh` walks a fixed `CATEGORIES` list and still symlinks each Skill to a **flat** `~/.claude/skills/<name>`, because Claude Code discovers Skills by bare directory name and does not read nested categories.

We rejected a flat repo because the top level had grown to fifteen sibling directories with no signal about which ones form the workflow and which are standalone. We rejected encoding the category in the Skill name, as in `kanban-project-planning`, because the name is what you type and `/project-planning` should stay short, and because moving a Skill between categories would then rename it.

The consequences: the category is repo-level metadata only, so Skill names must stay unique across categories; adding a category means adding it to the `CATEGORIES` array in `install.sh`; and moving a Skill between categories leaves a stale symlink, which `install.sh` now silently re-points when the old target is inside this repo.
