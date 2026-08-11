# Comment Convention

## Global rules

- Comments explain *why*, not *what*. The code already shows what it does.
- (optional: inline placement threshold, e.g. "inline only for single-statement clarifications")
- (optional: exceptions to WHY-not-WHAT, e.g. regex patterns, compliance annotations)

---

## <Language>

- **Style**: above-symbol / inline / both — (guidance on when inline is appropriate)
- **Format**: (doc-comment format, e.g. JSDoc / Javadoc / PEP 257 triple-quoted / godoc `//`)
- **Params**: all / public-API only / complex only / never
- **Returns**: always / non-obvious only / never
- **Exceptions**: always / public-API only / never
- **Local variables**: non-obvious only / never
- **Idiom**: (language-specific note, e.g. "exported symbols only; comment starts with symbol name")

---

## Python (example)

- **Style**: above-symbol; inline only for non-obvious single-line assignments
- **Format**: Google-style triple-quoted docstrings
- **Params**: public-API only
- **Returns**: non-obvious only
- **Exceptions**: public-API only
- **Local variables**: non-obvious only
- **Idiom**: docstring placed immediately after `def`/`class` line; one-liner for trivial functions, multi-section (Args / Returns / Raises) for public API
