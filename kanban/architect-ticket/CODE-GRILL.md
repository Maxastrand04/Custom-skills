# Code grill

`architect-ticket`'s grill. Run `grilling`'s rounds, frontier, and recommendations as that skill says, and ask each question in the format below. Code options are always on.

## Code or prose

Before each question, judge its level. A decision that must be settled before any code can exist, such as whether the change belongs in this repo at all, is asked in prose, in `grilling`'s format. Every other question is code-level and asked as code options.

## A code-level question

````
❓ **Q1** - **<question title>**: <one line saying what is being decided>

**Current**
```python
def refresh(token: str) -> Session: ...
```

**A**
```python
def refresh(token: Token) -> Session: ...
refresh(expired_token)        # raises TokenExpired
```

**B**
```python
def refresh(token: Token) -> Session | None: ...
refresh(expired_token)        # returns None
```

➡️ **A**, because every other entry point in `auth/` raises on a bad token.
````

- **Options are code.** Label them A, B, and on. Write each as a snippet in the project's language, using real names from the codebase.
- **One fenced block per snippet.** Each option and `Current` gets its own fenced block with the language tag. Its bold label sits alone on the line above, with a blank line before the label. Never indent code instead of fencing it, since indented code runs into the next label.
- **Interface options are signatures.** Bodies are `...`.
- **Guarantees are calls.** A call followed by its outcome as a trailing comment, such as `refresh(expired_token)        # raises TokenExpired`.
- **Trailing comments stand apart.** Put at least 8 spaces between the code and `#`. Within a block, line every trailing `#` up in one column.
- **Show what exists.** When the entry point already exists, put its current code above the options, under `Current`.
- **Outcome comments are the only comments.** Options carry no docstrings. The contract's docstring is written in Phase 2.
- **10 lines per option.** An option over 10 lines drops to signatures with `...` bodies. Still over 10 means the question covers too much, so split it.
- **The recommendation is one bold letter** and one sentence of why, after a blank line.

## Ambiguous Behaviour lines

Ask the line as a call through the settled stubs, then each possible reading as an outcome comment, one option per reading:

````
**A**
```python
login(user)        # ends the first session
```

**B**
```python
login(user)        # both sessions stay active
```
````

## Record conflicts

A PCR or ADR in the way is stated in two lines, then the decision:

```
ADR-0003 says: tokens never leave `auth/`.
The ticket wants: the admin panel reads the token directly.
```

Then ask the decision like any other question. Give no reasons or consequences. The record holds them.

## After a pick

A picked option is settled. It goes into the source files in Phase 2 and never appears in chat again.
