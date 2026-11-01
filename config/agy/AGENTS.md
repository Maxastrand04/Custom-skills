# Global Agent Instructions

## Rules
- Push back on user input and ensure a mutual understanding before writing.
- Check all output, file or chat, against the unslop skill before sending. No em dashes.
- Gloss every domain term not in ~/.claude/glossary.md, per the gloss-me skill. Project docs like CONTEXT.md never count as known terms.
- Do not spawn subagents unless the user explicitly requests delegation or an active skill requires it. Complete work directly in the main conversation.

## Working in a repo
Each rule applies only where its condition holds. Branch rules need git, ticket rules need a GitHub remote, record rules need `docs/adr/` or `docs/pcr/` to exist. A question or a code read triggers no branch or ticket rule.

### Records
- Before changing code, read every ADR in `docs/adr/` and every PCR in `docs/pcr/`. Both are binding.
- Read `CONTEXT.md` if it exists and use its terms for domain concepts.
- Never edit a PCR. Never write or amend an ADR. A decision worth recording goes to /grill-docs.
- If a PCR blocks the work, name the PCR and what it blocks, hand the user /challenge-pcr, and treat the PCR as standing.

### Layout
- Put a new file where a PCR says. With no PCR covering it, follow the repo's existing pattern, point the user at /grill-docs once per session, and ask before creating a new top-level directory.

### Branches and tickets
- Work on a branch, never on the default branch.
- Ticket work gets one branch per ticket with a draft ticket PR. A branch built by hand ends at /review-diff, then /pr-ticket.
- A small change with no ticket goes on its own branch and reaches the default branch through an ordinary PR the user reviews and merges.
- A change stops being small once it runs past a few lines, renames something other files call, or touches a record. Stop there and offer /new-ticket.

### Commits
- Commit messages and PR titles follow Conventional Commits.

### Precedence
- A PCR or the project's own instruction file beats this file on conventions. An active skill beats it on what that skill says it may do. Nothing lets an ordinary session edit a PCR.
