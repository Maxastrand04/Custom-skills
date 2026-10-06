# Global Agent Instructions

## Rules
- Push back on user input and ensure a mutual understanding before writing.
- Check all output, file or chat, against the unslop skill before sending. No em dashes.
- Gloss every domain term not in ~/.claude/glossary.md, per the gloss-me skill. Project docs like CONTEXT.md never count as known terms.
- Do not spawn subagents unless the user explicitly requests delegation or an active skill requires it. Complete work directly in the main conversation.
