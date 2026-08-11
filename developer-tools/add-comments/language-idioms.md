# Language Idioms

Per-language reference for canonical comment style. Use this during the grill to prompt the user with the idiomatic option for their language.

---

## Python

Triple-quoted docstrings (`"""..."""`) placed immediately after the `def` or `class` line — not before it. PEP 257 defines two forms: a one-liner (`"""Do X."""`) for trivial functions, and a multi-line form with a summary line, blank line, and body for everything else. The three common section styles are Google (indented `Args:` / `Returns:` / `Raises:` headers), NumPy (underlined headers), and Sphinx (`:param name:` / `:returns:` / `:raises ExcType:`). Pick one and apply it consistently.

---

## TypeScript / JavaScript

JSDoc (`/** ... */`) for symbols intended for documentation or tooling (IDEs, TypeDoc, JSDoc). Use `@param {type} name — description`, `@returns {type}`, and `@throws {ErrorType}` tags. Inline `//` for implementation notes inside function bodies. Plain `//` comments are not indexed by doc generators and should not duplicate what JSDoc already covers on the signature.

---

## CSS / HTML

CSS uses `/* */` block comments only — there is no doc-comment standard. Convention: place a `/* WHY */` comment above any non-obvious rule or block (e.g., a magic z-index, a workaround for a browser bug, a deliberate override). Avoid restating what the CSS already says.

HTML uses `<!-- -->` comments. There is no doc-comment idiom. Convention: add a comment above complex or non-obvious markup sections to explain intent or structural role, not to label things that are self-evident from tag names and class names.

---

## Go

Exported symbols (functions, types, constants, variables) must have a doc comment directly above the declaration with no blank line between the comment and the declaration. The comment starts with the symbol name: `// FuncName does X.` `godoc` and `pkg.go.dev` render these comments as the official documentation. Unexported symbols do not require doc comments; inline `//` notes inside function bodies are fine.

---

## Rust

`///` (three slashes) for outer doc comments on items (functions, structs, enums, traits, modules). `//!` for inner doc comments describing the enclosing item — typically used at the top of a module file or crate root. Both support Markdown and are rendered by `rustdoc`. Regular `//` comments are not rendered as documentation. By convention, public items in a library crate should have `///` doc comments.

---

## Java / Kotlin

Javadoc (`/** ... */`) placed above the declaration. Standard tags: `@param name description`, `@return description`, `@throws ExceptionType description`, `@deprecated reason`. The first sentence of the Javadoc comment becomes the summary shown in IDE tooltips and generated HTML. Inline `//` or `/* */` for implementation notes inside method bodies.

Kotlin uses KDoc, which shares the same `/** ... */` delimiter and placement rules as Javadoc. Tags: `@param`, `@return`, `@throws`, `@constructor`, `@sample`. KDoc bodies support Markdown.

---

## C / C++

Two common styles: Doxygen (`/** ... */` or `///` lines with `@brief`, `@param`, `@return` tags) and plain block comments (`/* ... */`). Doxygen comments are machine-readable and can generate HTML/PDF docs; plain block comments are not. Choose one style and apply it consistently across the project. Inline `//` is standard for single-line implementation notes.

---

## C#

XML doc comments (`/// <summary>...</summary>`) placed above the declaration. Standard elements: `<summary>`, `<param name="...">`, `<returns>`, `<exception cref="...">`. Visual Studio and Rider render these as IntelliSense tooltips; they are also consumed by `dotnet doc` tooling. Regular `//` or `/* */` for implementation notes. XML doc comments on public members are enforced by some analysers (e.g. `SA1600`).

---

## SQL

SQL uses `--` for single-line comments and `/* */` for multi-line block comments. There is no doc-comment standard. Convention: annotate queries when the logic is non-obvious — complex joins, subquery rationale, performance-driven choices (e.g., a forced index hint), or business rules embedded in a WHERE clause. Skip comments that merely restate what the SQL already reads clearly.
