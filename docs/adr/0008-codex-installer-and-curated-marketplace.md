# ADR-0008: Codex installer and curated marketplace

**Decision:** Codex has both installation routes. `install.sh --codex` offers all live category skills and links generated Codex copies into `~/.agents/skills/`. A Codex marketplace at `.agents/plugins/marketplace.json` points to `plugins/max/`. It ships the same skills as the Claude marketplace, read from the `max` plugin's `skills` list in `.claude-plugin/marketplace.json`, so the two cannot drift apart. Generated marketplace files are tracked. Personal output under `.codex-build/` is ignored. Claude Code and Antigravity keep their existing routes and default targets.

**Reason:** The author wants a personal selection through `install.sh` and a smaller shared set through the marketplace. Codex uses a separate invocation setting, and the maintained Claude sources must keep their own setting. A generated flat layout also resolves the shared-file references between categories. One builder keeps the two Codex outputs consistent.

**Consequence:** Codex source edits require a rebuild. The personal installer rebuilds automatically when run. GitHub Actions validates marketplace output on pull requests that touch it, and rebuilds it on every commit to the default branch, committing generated changes after successful checks. When the built skills differ from the commit that last set the plugin version, the same run raises the last number of that version so Codex installs a fresh copy. Local builds remain available through `python3 scripts/build-codex.py`. The publish job only stages `plugins/max/skills/` and `plugins/max/plugin.json`, skips unchanged output, and skips pushing when the branch has advanced. A shared file owned by an excluded skill can ship without exposing that skill. Both marketplaces include `unit-test-ticket` and `pr-ticket` so the ticket chain has its handoff stages. `ci/` and `archive/` are excluded.

This extends ADR-0005 and ADR-0007. ADR-0002's immediate live-edit property still applies to Claude Code and Antigravity, while Codex uses generated copies. ADR-0004's user-invoked split is preserved through `agents/openai.yaml` in the Codex outputs.

**Date:** 2026-10-07
