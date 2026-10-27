# ADR-0012: The release commit's push to main is not forced

**Decision:** The release workflow MUST push its `chore(release): vX.Y.Z` commit to main without force.

**Reason:** Unknown. Found as a comment in `.github/workflows/release.yml`, quoted:

> Not forced, so a main that moved ahead rejects the push.

**Consequence:** A main that gained a commit during the run rejects the push and stops the run. A forced push would erase that commit from main.

**Scope:** `.github/workflows/release.yml`, the "Commit the version to main" step

**Status:** found

**Date:** 2026-10-27
