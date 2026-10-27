# ADR-0011: The release checkout has full history

**Decision:** The checkout in `.github/workflows/release.yml` MUST fetch the full history and tags (`fetch-depth: 0`).

**Reason:** Unknown. Found as a comment in `.github/workflows/release.yml`, quoted:

> The version calculator reads every commit since the last tag.

**Consequence:** A shallow checkout hides the `vX.Y.Z` tags and the commits since them, so `scripts/release.py plan` would see no earlier release and plan `1.0.0` again.

**Scope:** `.github/workflows/release.yml`, the `release` job's checkout step

**Status:** found

**Date:** 2026-10-27
