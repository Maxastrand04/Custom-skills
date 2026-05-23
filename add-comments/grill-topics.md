# Grill Topics

The convention grill runs before any source files are read or written. It is a pure interview. No files are touched until the user explicitly approves the finalized convention.

**Sequencing pin:** The grill does NOT begin until the user has confirmed which languages are in scope. After each topic, the skill records the answer and moves to the next topic without re-asking confirmed answers.

---

## Topic 1 — Inline vs above-symbol placement

Ask the user:

> Should comments appear above the symbol declaration (above-symbol) or on the same line as code (inline)? Or are both allowed? If both, when is inline preferred over above-symbol?

Record:
- Default placement for each language in scope.
- Whether inline is allowed at all, and if so, the threshold (e.g. "only for short clarifications on a single statement").

---

## Topic 2 — Per-language docstring / doc-comment format

For each language the user names as in scope, ask:

> What doc-comment format do you prefer for `<language>`?

Prompt with the common options for that language if the user is unsure:

- Python: Google style / NumPy style / Sphinx (`:param:`) / plain triple-quoted
- TypeScript / JavaScript: JSDoc (`/** */`) / plain `//`
- Go: plain `//` starting with the symbol name (godoc) / no preference
- Rust: `///` outer doc comments / `//!` inner doc comments (modules)
- Java: Javadoc (`/** */`) / plain `//`
- C / C++: Doxygen (`/** */` or `///`) / plain `/* */`
- C#: XML doc comments (`/// <summary>`) / plain `//`

Record the chosen format per language.

---

## Topic 3 — WHY not WHAT

State the principle and confirm agreement:

> Comments should explain *why* a decision was made, not *what* the code does — the code already shows that. Do you agree? Are there any exceptions (e.g. regex patterns, non-obvious algorithms, required compliance annotations)?

Record:
- Whether the user agrees with WHY-not-WHAT as the default.
- Any categories of exception the user names.

---

## Topic 4 — Parameters, returns, exceptions, and local variables

Ask:

> Should function parameters be documented in comments? Return values? Raised or thrown exceptions? Local variables? And at what threshold — all functions, public API only, or only complex/non-obvious ones?

Cover each axis separately if the user gives a blanket answer, then confirm:

- **Params**: all / public-API only / complex only / never
- **Returns**: always / non-obvious only / never
- **Exceptions**: always / public-API only / never
- **Local variables**: only non-obvious ones / never

Record per-language if the user's answers differ across languages.

---

## Topic 5 — Per-language idiomatic style

For each language in scope, ask:

> Are there idiomatic conventions for `<language>` that you want enforced — for example, Go exported-function comments starting with the function name, or Rust `///` for public items only?

Consult `language-idioms.md` internally to prompt with the canonical idiom if the user is unsure, but do not paste the reference at the user — summarise it in a single sentence as a prompt option.

Record any per-language idiom preferences that override or extend the format chosen in Topic 2.

---

## Convention approval

After all topics are covered, present the filled-in `comment-convention.md` skeleton for review. The skill halts and waits for explicit approval before writing the file.

Accepted approval phrases:
- `approve`
- `looks good, continue`

No other phrasing advances the workflow. After approval, write `comment-convention.md` to the user-chosen location (project root by default).
