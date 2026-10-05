# behaviour

Skills that change how the agent talks rather than what it builds. Claude invokes these on its own, and other skills borrow them by name.

| Skill | What it does |
|-------|--------------|
| `grilling` | Interviews you about a plan one round at a time, with a recommended answer for each question, until the plan is settled. |
| `unslop` | Removes AI tells from writing: puffery, em dashes, filler, passive voice. |
| `talk-to-middleschooler` | Wording rules for a reader who knows nothing about the subject. Every term glossed before use, no equations. |
| `talk-to-highschooler` | Wording rules for a reader with algebra and basic programming. Terms glossed once, notation kept. |
| `science-output` | Format rules for math: every expression in a `$$` block with its symbols named underneath. Not in the plugin. |
