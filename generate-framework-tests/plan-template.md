# Plan Template

This file defines the shape of the combined approval plan that Claude presents to the user before writing any test files. Claude reads this file at runtime and constructs a plan matching the structure below. No test files are written until the user approves.

---

## Required sections (in order)

Every plan must contain these four sections, in this order:

1. Framework choice
2. Files to create
3. Files to update
4. Per-file cases

---

## 1. Framework choice

Before showing the full plan, Claude must determine and state the test framework.

**If a framework is already detected** (e.g. pytest in pyproject.toml, Jest in package.json, RSpec in Gemfile): state it as a fact. No confirmation needed unless the user may want to switch. Example:

> Framework: **pytest** (detected in pyproject.toml)
> Test command: `pytest`

**If no framework is detected**: do not show the full plan yet. First ask a mini-confirm:

> No test framework detected. Propose **pytest**. Confirm or name another.

Wait for the user's response, then show the full plan with the confirmed framework.

Always include the test command that will be used after the files are written.

---

## 2. Files to create

A list of source files that have no corresponding test file yet. Each row maps source path to planned test path.

Format each entry as:

```
src/auth/login.py → tests/auth/test_login.py  [NEW]
```

Show one entry per line. If there are no new files to create, omit this section or write "None."

---

## 3. Files to update

A list of existing test files where drift was detected between the source and the recorded manifest. Each entry shows the source path, the existing test path, and per-file drift annotations.

Drift is grouped into three buckets per file:

- `+add` — cases that will be added (new behaviour in source not yet tested)
- `-remove` — cases in the manifest that are no longer relevant (source behaviour removed)
- `~update` — cases in the manifest that need updating (source signature or behaviour changed)

Format each entry as:

```
src/utils.py → tests/test_utils.py
  +add: test_parse_empty_input
  ~update: test_parse_valid_json (return type changed)
  -remove: test_legacy_format
```

Omit buckets that have no entries. If there are no files to update, omit this section or write "None."

---

## 4. Per-file cases

For every file in sections 2 and 3, list the planned test cases. Cases are described in plain English — no code, no signatures, just the case name and a one-line intent.

Format each file block as:

```
tests/auth/test_login.py:
  - test_login_valid_credentials — returns user object on success
  - test_login_wrong_password — raises AuthError
  - test_login_missing_username — raises ValueError
```

For files to update, list only the cases being added or changed. Cases that remain unchanged are not repeated here.

---

## No-writes-before-approval

State this explicitly at the end of the plan:

> No files will be written until you approve this plan. You can edit the plan inline before approving: add or drop cases, rename cases, change test file paths, or remove entire files from scope. Reply with any affirmative response ("looks good", "approve", "yes", etc.) to proceed.

After the user approves, Claude writes all files in the plan in the order they appear.
