# preview-loop

Per-symbol preview and approve loop. Called by `SKILL.md → preview-walk` for each symbol in scope.

---

## Preview format

Show a fenced code block containing:

- The symbol being commented, with the new or changed comment in place
- Enough surrounding context to make the target unambiguous — at minimum the enclosing class signature (if any) and a few lines above and below the symbol

Label the block with the language identifier. Do not show a diff; show the final proposed state.

---

## Prompt options

After each preview, present exactly four options:

| Option | Behavior |
|---|---|
| `approve` | Accept the proposed comment as shown; stage it for this file |
| `edit` | Let the user tweak the comment inline before staging; re-render the symbol preview after the edit and confirm before staging |
| `skip` | Leave this symbol unchanged; move to the next symbol |
| `accept-file` | Approve all remaining symbols in this file without further per-symbol prompts; stage them all |

Wait for one of these four responses. Do not advance on silence or ambiguous input — re-present the options.

---

## Per-file batch writes

Approved and edited changes are held in memory as the walk progresses through a file. They are flushed to disk as a single write only when the file is fully complete — meaning every symbol in the file has been either approved/edited or skipped.

This ensures that a mid-session abort while working through file N does not partially corrupt file N.

---

## Mid-session abort semantics

If the user aborts (closes the session, types `abort`, `cancel`, or equivalent) mid-file:

- Discard all staged-but-not-yet-flushed changes for the current file.
- All previously completed files — those that were fully walked and flushed — remain written and are not rolled back.

---

## Existing-comment validation

The skill does **not** perform a blanket scan of existing comments. Existing-comment validation only fires when the skill already intends to add or change a comment on a given symbol. Comments on symbols that are not in scope for a change are left untouched and no warning is shown.
