# vim-bindings

Prompts that Zed keys run through `claude -p`, built in [zed-agent-commands](https://github.com/Maxastrand04/zed-agent-commands). Each skill takes a file path, a cursor line and the selected text as arguments, and `rewrite-selection` also takes the code rules. The Zed task, not the skill, sets the model and the tools. You can also type one as a slash command in an agent panel thread.

| Skill | What it does |
|-------|--------------|
| `explain-selection` | Explains the selected code and flags a hidden side effect or edge case. |
| `rewrite-selection` | Rewrites the selected code to follow the code rules, in place, keeping its behaviour. |
