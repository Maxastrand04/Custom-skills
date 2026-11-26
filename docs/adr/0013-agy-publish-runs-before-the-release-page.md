# ADR-0013: The Antigravity publish runs before the release page

**Decision:** In `.github/workflows/release.yml`, the "Publish the Antigravity tree" step MUST run before the "Create the release page" step.

**Reason:** Unknown. Found as a comment in `.github/workflows/release.yml`, quoted:

> Before the release page: gh release create fails on a re-run, so a publish placed after it would never be retried.

**Consequence:** Moving the publish after `gh release create` means a run that failed to publish can never publish on a re-run, because the re-run stops at the release page that already exists.

**Scope:** `.github/workflows/release.yml`, the `release` job's "Publish the Antigravity tree" step

**Status:** found

**Date:** 2026-11-26
