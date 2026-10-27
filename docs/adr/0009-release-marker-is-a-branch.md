# ADR-0009: The release marker is a branch

**Decision:** The release marker both marketplaces serve from MUST be the branch `release`, and the release workflow MUST only ever fast-forward it to a release commit on main, never force-push it or replace it with a tag.

**Reason:** The alternative was a moving tag, such as `latest`, deleted and recreated each release. Git refuses by default to update a tag a clone already holds, so a user's cached marketplace could stay on an old release with no error. A branch that only moves forward along main's history is something every git client fetches. Each version still gets its own `vX.Y.Z` tag, created with its GitHub release page.

**Consequence:** Users add `Maxastrand04/Custom-skills#release` in Claude Code and `--ref release` in Codex, and every install instruction says so. Every commit on `release` is also on main. A fix that skips main and lands on `release` directly breaks the fast-forward and the next release run. Renaming the branch strands every user who added it.

**Date:** 2026-10-27
