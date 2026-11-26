# ADR-0010: Release decisions live in scripts/release.py

**Decision:** The release workflow MUST take every release decision, meaning the next version, the release notes, and the manifest edits, from `scripts/release.py`, and its YAML MUST only run git, `gh`, that script, and build scripts that build and check a package without deciding anything about the release, such as `scripts/build-codex.py` and `scripts/build-agy.py`. The YAML decides nothing itself.

**Reason:** The alternative was the whole release in workflow YAML and inline bash, which is shorter but leaves the version rules where no test can reach them. A stdlib-only script, shaped like `scripts/build-codex.py`, lets `unittest` check the rules against plain lists of commit messages without a repository or GitHub.

**Consequence:** A change to how versions are picked or notes are grouped is a change to `scripts/release.py` and its tests, never to `.github/workflows/release.yml`. The YAML keeps what tests can't cover: the branch check, the push, moving the marker, and the release page. Those stay manual checks. The script MUST stay runnable on the Python version the workflows set up, with no packages to install.

**Date:** 2026-11-26
