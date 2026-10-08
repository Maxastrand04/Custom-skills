---
name: launch
description: Queues an architected ticket for kanban-ci. Adds the handoff trailer to the Architect commit, pushes the branch, and labels the issue ci:queued.
disable-model-invocation: true
---

# launch

Run after `/architect-ticket` commits. Marks the red branch ready for the kanban-ci loop and queues it. It starts nothing. The nightly run picks the ticket up, or the user starts it with `gh workflow run kanban-ci`.

Word every message per the `gloss-me` skill.

## 1. Check the branch

Take the current branch, or the one named in the invocation. Halt, naming the check, unless all of these hold:

- **The name carries an issue number**, as in `42-oauth-admin-login`.
- **The working tree is clean.** Uncommitted changes would be left behind.
- **`HEAD` is the architect commit.** Its subject starts `Architect #<N>:` and `<N>` matches the branch.
- **It isn't queued already.** `git log -1 --format='%(trailers:key=Handoff-To,valueonly)'` prints nothing.
- **The project calls the workflow.** `.github/workflows/kanban-ci.yml` exists on the default branch, `git show origin/HEAD:.github/workflows/kanban-ci.yml`. If it doesn't, point at `ci/README.md` in the Custom-skills repo for setup.

## 2. Add the trailer

If `HEAD` isn't on the remote yet, amend it in place:

```
git commit --amend --no-edit --trailer "Handoff-From: architect-ticket" --trailer "Handoff-To: implement-ticket"
```

If it was already pushed, never amend a pushed commit. Add an empty commit instead:

```
git commit --allow-empty -m "Launch #<N>" --trailer "Handoff-From: architect-ticket" --trailer "Handoff-To: implement-ticket"
```

## 3. Push and queue

```
git push -u origin <branch>
gh label create ci:queued --color FBCA04 --description "Waiting for the kanban-ci loop" 2>/dev/null || true
gh issue edit <N> --add-label ci:queued
```

## 4. Report

```
Branch   42-oauth-admin-login, pushed
Issue    #42 labelled ci:queued
Runs     next scheduled run, or now with: gh workflow run kanban-ci --ref 42-oauth-admin-login
```
