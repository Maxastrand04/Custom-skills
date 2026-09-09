# ADR-0002: Install via symlink, not by cloning into `~/.claude/skills/`

**Decision:** `install.sh` MUST create a symlink from `~/.claude/skills/<name>` to each Skill directory in the repo. The repo MUST NOT be cloned directly into `~/.claude/skills/`.

**Reason:** Cloning into `~/.claude/skills/` would pin the repo to a fixed filesystem location, force `.git/`, `README.md`, and tooling files to sit alongside live Skills, and stop the repo being moved or backed up on its own. Symlinks also keep edits live, so there is no install or sync step while iterating on a Skill, and they match the pattern already used by `~/.agents/skills/`.

**Consequence:** The repo can live at an arbitrary path, such as `~/GitHub/Custom-skills`, and an edit to a `SKILL.md` takes effect on the next invocation with nothing re-run. In exchange, the installed Skills depend on the repo staying where it is: move or delete it without re-running `install.sh` and every symlink dangles.

**Date:** 2026-08-11
