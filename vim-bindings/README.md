# vim-bindings

Prompts that Zed keys run through `claude -p`, built in [zed-agent-commands](https://github.com/Maxastrand04/zed-agent-commands). Each skill takes a file path, a cursor line and the selected text as arguments, and `rewrite-selection`, `implement-selection` and `pseudocode-selection` also take the code rules. The Zed task, not the skill, sets the model and the tools. You can also type one as a slash command in an agent panel thread.

| Skill | What it does |
|-------|--------------|
| `explain-selection` | Explains the selected code and flags a hidden side effect or edge case. |
| `implement-selection` | Writes a working body for the selected code from its docstring and its callers in the file, in place. |
| `pseudocode-selection` | Replaces the selected pseudocode with real code that matches the rest of the file, in place. |
| `rewrite-selection` | Rewrites the selected code to follow the code rules, in place, keeping its behaviour. |
