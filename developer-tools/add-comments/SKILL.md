---
name: add-comments
description: Grills out a persisted comment-convention.md, then walks the code symbol by symbol with an approve, edit, or skip preview.
disable-model-invocation: true
---

# add-comments

Grill the user into a persisted `comment-convention.md`, then walk source files in scope and run a per-symbol preview-and-approve loop to add or update comments in line with the convention.

This skill is markdown-only orchestration. Read bundled files at runtime. Do not assume their contents from this document:

- `grill-topics.md` holds the topics covered in the full multi-language grill and the scoped single-language grill.
- `language-idioms.md` holds the per-language idiomatic comment style applied during the preview walk.
- `preview-loop.md` holds the per-symbol preview and approve UI, plus batch-write semantics.
- `template_comment_convention.md` holds the schema and section layout for `comment-convention.md`.

---

## Invocation

Handle exactly six entry forms:

1. **No args.** Prompt the user: "What would you like to comment? Provide a file, a folder, or a flag (`--edit-convention`, `--new-convention`)."
2. **`<file>`.** Run `ensure-convention`, then run `preview-walk` scoped to that file.
3. **`<file> <symbol>`.** Run `ensure-convention`, then run `preview-walk` scoped to that single symbol only.
4. **`<folder>`.** Run `ensure-convention`, then run `preview-walk` over all source files under the folder.
5. **`--edit-convention`.** Locate the nearest-ancestor `comment-convention.md` from the current working directory. If found, open it for editing and stop. If none found, error: "No `comment-convention.md` found in any ancestor directory. Run `--new-convention` to create one."
6. **`--new-convention`.** Run the full multi-language grill, per `grill-topics.md`, and write a new `comment-convention.md` at a user-chosen location. Do NOT auto-import from any existing convention file unless the user explicitly asks.

---

## ensure-convention

Run this sub-flow before any `preview-walk`.

1. Walk up the directory tree from the target path, looking for `comment-convention.md`.
2. **Found.** Use it as the active convention. Read it, and do not modify it yet. Proceed to `preview-walk`.
3. **Not found.** Run the full multi-language grill, with topics in `grill-topics.md`, and write a new `comment-convention.md`. Ask the user where to place it before writing. Follow the schema in `template_comment_convention.md`.

---

## preview-walk

Walk source files in scope. For each symbol in each file, run the per-symbol loop defined in `preview-loop.md`. Apply the language's idiomatic comment style from `language-idioms.md` when generating proposed comments.

### Language detection

Detect language by file extension:

| Extension(s) | Language |
|---|---|
| `.py` | Python |
| `.ts`, `.tsx` | TypeScript |
| `.js`, `.jsx` | JavaScript |
| `.go` | Go |
| `.rs` | Rust |
| `.java` | Java |
| `.kt` | Kotlin |
| `.c`, `.h` | C |
| `.cpp`, `.hpp`, `.cc` | C++ |
| `.cs` | C# |
| `.css` | CSS |
| `.html` | HTML |
| `.sql` | SQL |

Shebang/content sniffing only as fallback for extensionless files. Unknown extension → prompt the user: "Unknown file type for `<filename>`. What language is this?" If the user cannot answer, skip the file.

### Non-source file handling

Skip the following silently, and do not prompt the user:

- `.md`, `.txt`
- Config files: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.env`, `.cfg`, `.conf`

Source files with no functions or methods (e.g., a file containing only constants or type aliases) → prompt the user with a recommendation to skip.

### Missing-language behavior

If the active `comment-convention.md` has no section for the target file's language:

1. Stop the walk.
2. Run a **scoped single-language grill**, covering only the topics for this one language, per `grill-topics.md`. Do NOT run the full multi-language grill again.
3. Append a new `## <Language>` H2 section to the existing `comment-convention.md`.
4. Resume the walk.

---

## Skip list: vendored and generated directories

During folder walks, skip these directories silently:

**VCS / editor:** `.git`, `.idea`, `.vscode`, `.vs`

**Python:** `__pycache__`, `venv`, `.venv`, `.tox`, `.pytest_cache`, `.mypy_cache`, `*.egg-info`

**JS / TS:** `node_modules`, `dist`, `build`, `.next`, `.nuxt`, `out`, `.cache`, `coverage`

**Go:** `vendor`, `bin`

**Rust:** `target`

**Java / Kotlin:** `target`, `build`, `.gradle`, `out`

**C / C++:** `build`, `cmake-build-*`, `out`, `bin`, `obj`

**C#:** `bin`, `obj`

**Generic:** `dist`, `build`, `out`, `tmp`

Anything else that looks generated (e.g., a directory named `generated`, `autogen`, or containing only files with a `DO NOT EDIT` header) → prompt the user: "Looks generated: `<dir>`. Skip it?"

---

## Do not

- Do **not** auto-import from an existing convention file unless the user explicitly requests it when running `--new-convention`.
- Do **not** flush file changes to disk mid-file. Batch writes are owned by `preview-loop.md`.
- Do **not** validate or alter existing comments on symbols the skill has no intent to touch.
- Do **not** add features beyond the six invocation forms above.
