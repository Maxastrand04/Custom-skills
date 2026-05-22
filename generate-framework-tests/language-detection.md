# Language Detection

Determines the target language and test framework for a project before any test generation begins. All rules in this file apply globally — they are evaluated before per-file decisions are made.

---

## Mirror existing convention rule

**This rule takes precedence over every per-language default below.**

Before applying any default placement or naming rule, scan the project for existing test files:

1. Look for files matching patterns such as `*_test.*`, `*.test.*`, `test_*.*`, or files inside directories named `tests/`, `test/`, `__tests__/`.
2. If any existing test files are found, extract:
   - Their naming pattern (e.g. `test_<name>.py` vs `<name>_test.py`, `*.test.ts` vs `*.spec.ts`).
   - Their directory layout (co-located vs. separate `tests/` tree, mirroring source structure or flat).
3. Mirror that layout exactly for all newly generated files. Do not mix conventions within a single project.
4. Only fall back to the per-language defaults below when the project has **no existing test files at all**.

---

## Python

**Detection signals:** any of the following present in the project root or a subdirectory:
- `pyproject.toml`, `setup.py`, `setup.cfg`, or `requirements*.txt`
- `.py` source files

**Default framework:** `pytest`

**Default test-file placement:** `tests/` directory mirroring the source structure.

| Source file | Test file |
|---|---|
| `src/foo/bar.py` | `tests/foo/test_bar.py` |
| `mypackage/utils.py` | `tests/utils/test_utils.py` |

**Test-command invocation:** scope the run to just the files written in this session.

```
pytest tests/foo/test_bar.py
```

**Import style:** standard pytest — use plain `def test_*` functions; use `pytest.fixture` for shared setup; import `pytest` only when parametrize, fixtures, or raises are needed.

---

## JavaScript / TypeScript

**Detection signals:**
- `package.json` present in the project root
- `.js`, `.ts`, `.jsx`, or `.tsx` source files

**Framework detection order** (check `package.json` `devDependencies` and `scripts`):

1. `vitest` listed → use **Vitest**
2. `jest` listed → use **Jest**
3. `node:test` referenced in scripts → use **Node built-in test runner**
4. None found → default to **Vitest**

**Default test-file placement:** co-located next to the source file.

| Source file | Test file |
|---|---|
| `src/utils.ts` | `src/utils.test.ts` |
| `src/components/Button.jsx` | `src/components/Button.test.jsx` |

**Test-command invocation:** derive the package manager from the lockfile present at the project root.

| Lockfile | Command |
|---|---|
| `package-lock.json` | `npm test` |
| `pnpm-lock.yaml` | `pnpm test` |
| `yarn.lock` | `yarn test` |
| None found | `npx vitest run <paths>` |

When invoking the runner directly, scope to the just-written file paths:

```
npx vitest run src/utils.test.ts
```

**TypeScript note:** read `tsconfig.json` for `module` and `target` settings before generating TS tests. Match import style (`import` vs `require`) and output target to what the project already uses.

---

## Go

**Detection signals:**
- `go.mod` present
- `.go` source files

**Framework:** built-in `testing` package — no external framework required.

**Default test-file placement:** co-located in the same package directory as the source file.

| Source file | Test file |
|---|---|
| `internal/auth/token.go` | `internal/auth/token_test.go` |
| `pkg/parser/parser.go` | `pkg/parser/parser_test.go` |

**Test-command invocation:** scope to the affected package using `./...` suffix.

```
go test ./internal/auth/...
```

**Default pattern:** use table-driven tests. Each test function declares a slice of structs (one per case) and ranges over it with `t.Run`. Apply this pattern for all new test functions unless the existing convention in the project differs.

---

## Rust

**Detection signals:**
- `Cargo.toml` present
- `.rs` source files

**Framework:** built-in `#[test]` and `#[cfg(test)]` — no external crate needed by default.

**Default test-file placement:**

- **Unit tests:** inline in the module being tested, inside a `#[cfg(test)] mod tests { ... }` block at the bottom of the source file.
- **Integration tests:** separate file in the `tests/` directory at the crate root.

| Scope | Location |
|---|---|
| Unit test for `src/parser.rs` | `#[cfg(test)] mod tests { ... }` at the bottom of `src/parser.rs` |
| Integration test | `tests/parser_integration.rs` |

**Test-command invocation:** scope to affected test names using the filter argument.

```
cargo test <test_name_filter>
```

Example: `cargo test parser::tests::` to run only the parser unit tests.

**Integration test note:** each integration test file in `tests/` is compiled as a separate crate. Place integration tests in `tests/<name>.rs`; do not add a `mod tests` wrapper inside these files.

---

## Java

**Detection signals:** any of the following present:
- `pom.xml` (Maven project)
- `build.gradle` or `build.gradle.kts` (Gradle project)
- `.java` source files

**Default framework:** JUnit Jupiter (JUnit 5)

**Framework version note:** before generating any test, read `pom.xml` or `build.gradle` to check which JUnit version is already declared as a dependency. Match that version — do not assume JUnit 5 if the project declares JUnit 4.

**Default test-file placement:** mirrors the source tree under `src/test/java/`.

| Source file | Test file |
|---|---|
| `src/main/java/com/example/Foo.java` | `src/test/java/com/example/FooTest.java` |
| `src/main/java/com/example/bar/Baz.java` | `src/test/java/com/example/bar/BazTest.java` |

**Test-command invocation:**

| Build tool | Command |
|---|---|
| Maven | `mvn test -pl . -Dtest=FooTest` |
| Gradle | `gradle test --tests com.example.FooTest` |

Scope the command to the specific test class written in this session. Do not run the full suite.

---

## Unknown language — escape hatch

When the language cannot be detected from the signals above, or when the detected language is not in the supported list:

1. Surface the detected language (or `"unknown"` if none could be determined) to the user.
2. Ask:

   > Detected language: `<language>`. This skill does not have built-in support for it. Name a test framework to use, or say **skip** to abort.

3. If the user names a framework, proceed with best-effort test generation using that framework's idioms. Apply the mirror-existing-convention rule first; otherwise ask the user for placement and naming preferences before generating files.
4. If the user says **skip**, exit cleanly without writing any files.

Do not guess or silently fall back. Always surface the ambiguity and wait for an explicit decision.
