# Exploration Heuristics

## Source-Root Detection

Scan the working directory for common source-root candidates in this priority order:

1. `src/`
2. `lib/`
3. `app/`
4. `packages/` (monorepo — each child is a separate root)
5. Project root itself (if none of the above exist)

After identifying candidates, **always present them to the user and ask which to use.** Do not silently pick one. Example prompt:

> Detected source roots: `src/`, `lib/`. Which should I use? (or specify a different path)

---

## Classifier Rules

Map signals found in each file to an agent job:

| Signal | Agent Job |
|---|---|
| No IO imports; pure function signatures only | `unit` |
| Imports from `fs`, `path`, `os`, database clients (e.g. `pg`, `mongoose`, `prisma`, `knex`, `sqlite3`), HTTP clients (e.g. `axios`, `node-fetch`, `got`, `http`, `https`), or network utilities | `integration` |
| File name or export matches `Component`, `Handler`, `Controller`, `Route`, or framework entry points (e.g. React/Vue/Svelte components, Express routers) | `behavior` |

Rules are evaluated top-to-bottom; the first match wins. If multiple signals conflict, prefer the higher-specificity job (`behavior` > `integration` > `unit`).

---

## Denylist

Exclude any file or directory whose path matches any of the following patterns. Do not explore, classify, or generate tests for excluded paths.

| Pattern | Reason |
|---|---|
| `node_modules/` | Third-party dependencies |
| `dist/` | Build output |
| `build/` | Build output |
| `.next/` | Framework build cache |
| `vendor/` | Vendored dependencies |
| Any file or directory starting with `.` (dotfiles/dotdirs) | Config/hidden files |
| `*.config.*` | Configuration files |
| `*.generated.*` | Auto-generated files |

---

## Path Mapping

Test file paths are derived from source file paths using this rule:

```
<source-root>/foo/bar.ext  →  tests/foo/bar.md
```

Steps:
1. Strip the source root prefix from the source file path.
2. Replace the file extension with `.md`.
3. Prepend `tests/`.

Example: `src/api/users.ts` with source root `src/` → `tests/api/users.md`

The `tests/` directory is always relative to the project root, not the source root.

---

## Symbol Extraction

Symbols (functions, classes, exported identifiers) are extracted using **regex patterns only**.

- No AST parsing. AST-based tools are explicitly forbidden.
- No language-specific parsers (TypeScript compiler API, Babel, tree-sitter, etc.).
- Extraction uses line-by-line regex matching against common declaration patterns.

Example patterns (illustrative, not exhaustive):

- `export (async )?function \w+`
- `export (default )?(class|const|let|var) \w+`
- `def \w+\(` (Python)
- `func \w+\(` (Go)
- `public (static )?(void|[A-Z]\w+) \w+\(` (Java/C#)

Regex extraction is intentionally approximate. It may miss edge cases (e.g. multi-line signatures, decorators). This is acceptable — completeness is not required, only a best-effort symbol list to seed the test template.
