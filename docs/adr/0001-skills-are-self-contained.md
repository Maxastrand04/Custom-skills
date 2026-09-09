# ADR-0001: Skills are self-contained

**Decision:** Every file a Skill references MUST live inside a Skill directory, its own or a sibling's, and MUST be referenced by a relative path. A sibling's file may be referenced only where that file declares itself a shared contract in its own opening lines, and a Skill's `SKILL.md` is never a shared contract.

**Reason:** This narrows an earlier decision that required every referenced file to live inside the *referencing* Skill's own directory. That rule was written in terms of path shape, but the alternative it actually rejected was a top-level `templates/` directory, meaning a shared resource owned by no Skill and sitting outside the install unit. A sibling's bundled file is not that. It has an owner, and symlinking that owner still brings it along, so the original argument never reached this case.

Six Skills were already referencing siblings and none had copied anything, so the rule forbade the practice the repo runs on and could not be cited. The compliant alternative was six copies of `ADR-FORMAT.md` that all have to agree, and copies of a contract diverge: a reader list inside that very file had gone stale, naming `map-epic` as an ADR writer when it writes none.

We rejected the looser form, any file in any sibling, because it makes every Skill's internals a public API by default and gives no signal before a change breaks a dependent. We rejected requiring an owner to list its readers, because that is a second copy of the dependency graph that nothing checks, and it is exactly the list that just rotted.

**Consequence:** A Skill can now fail at runtime because of a sibling. `refactor-ticket` breaks if `codebase-rules` is renamed, uninstalled, or moved to `archive/`, which `install.sh` never symlinks. Owning a shared contract also costs freedom: its owner can no longer rename or restructure it without checking who reads it, and there is deliberately no list to check, so that means grepping.

Publication is one declaration and nothing more, so a bundled file with no such line stays private and may not be reached from outside. In a diff, a breach looks like a `../` reference to a file that never declares itself shared, a `../` reference to any `SKILL.md`, or a referenced path that leaves the Skill directories entirely.

**Date:** 2026-09-02
