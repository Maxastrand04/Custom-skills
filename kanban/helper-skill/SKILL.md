---
name: helper-skill
description: Holds copies of base skill files the kanban skills read. Never run it. It only carries files.
disable-model-invocation: true
user-invocable: false
---

# helper-skill

This folder carries files, not instructions. Kanban skills read the files here with a `../helper-skill/` path, so they work even when the base skills are installed as a separate plugin.

Every file is a copy of a base skill's file:

| Copy | Original |
|---|---|
| `ticket-pr.md` | `pr-ticket/ticket-pr.md` |
| `RECORD-FORMAT.md` | `grill-docs/RECORD-FORMAT.md` |
| `ticket-shapes.md` | `new-ticket/ticket-shapes.md` |

Edit the original, never the copy. Then run `python3 scripts/sync-helper-skill.py`. A test fails while any copy differs from its original.
