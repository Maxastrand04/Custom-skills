---
name: eli10
description: Turn on learner mode for the rest of the session — everything explained to a sharp high schooler, algebra and basic programming assumed, domain terms glossed on first use.
disable-model-invocation: true
---

# eli10

Invoke the `talk-to-highschooler` skill for the language rules; this document supplies only the mode.

## Persistence

ACTIVE EVERY RESPONSE from now on. No drift back to normal prose after a few turns. Still active if unsure. Still active inside other skills invoked later in the session.

Off only when the user says "stop eli10" or "normal mode".

If the user says the level is still too high, switch to `eli5` and stay there instead.
