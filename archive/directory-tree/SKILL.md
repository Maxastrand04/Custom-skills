---
name: directory-tree
description: >
  Render the current project's directory structure as a markdown tree,
  excluding .gitignore'd paths. Use when the user says "directory tree",
  "show the file tree", "show directory structure", "refresh the tree",
  "print the tree", "list the project structure", or asks to visualise
  the folder layout of the current project.
---

# directory-tree

Renders the working directory as a fenced markdown tree, using git to honour `.gitignore`. Optionally writes the tree to a file.

## Invocation

- `/directory-tree` — print tree to the conversation
- `/directory-tree <file path>` — print tree and also write it to `<file path>`

---

## Step 1 — detect git

Run:

```
git rev-parse --is-inside-work-tree
```

- Exit 0, output `true` → **Step 2a (git mode)**
- Any other result → **Step 2b (fallback mode)**

---

## Step 2a — git mode

Run:

```
git ls-files --cached --others --exclude-standard
```

This returns every tracked and untracked-but-not-ignored file relative to the repo root. Use this flat list as the sole source of paths for the tree. Do not consult `.gitignore` directly or implement any ignore logic.

Build the tree from the returned paths:
- Directories before files at each level, both sorted alphabetically.
- Root line: the repo directory name (from `basename $(git rev-parse --show-toplevel)`).

---

## Step 2b — fallback mode (no git)

Emit this warning before the tree:

> **Note:** not inside a git repository — `.gitignore` filtering is unavailable. Showing all files (`.git/` excluded).

Walk the working directory recursively, excluding `.git/` at every depth. Sort directories before files, alphabetically at each level. Root line: `.`

---

## Step 3 — render

Emit the tree inside a fenced code block (triple backtick, no language tag):

```
<repo-name or .>
├── dir/
│   ├── subdir/
│   │   └── file.ext
│   └── file.ext
└── file.ext
```

Use standard box-drawing characters (`├──`, `│`, `└──`).

If the file list is empty (no non-ignored files): emit a minimal tree containing only the root line. Do not emit an error.

---

## Step 4 — optional file write

If an argument (file path) was supplied:
1. Write the fenced tree (same content as Step 3) to that path, overwriting if it exists.
2. Confirm: "Tree written to `<path>`."

If no argument was supplied, skip this step.
