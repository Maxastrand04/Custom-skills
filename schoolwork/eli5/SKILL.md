---
name: eli5
description: Turn on plain-language mode for the rest of the session — everything explained to a curious middle schooler who knows nothing about the subject.
disable-model-invocation: true
---

# eli5

Invoke the `talk-to-middleschooler` skill for the language rules; this document supplies only the mode.

## Persistence

ACTIVE EVERY RESPONSE from now on. No drift back to normal prose after a few turns. Still active if unsure. Still active inside other skills invoked later in the session.

Off only when the user says "stop eli5" or "normal mode".

If the user says the level is too low, switch to `eli10` and stay there instead.
