# ADR-0014: Station subagents resume at the halted step

**Decision:** When `tdd-ticket` starts a fresh subagent for a station that halted, the starting prompt MUST name the step the station halted at, the commits it already made, and the answer, and the subagent MUST continue from that step rather than rerun the station from the top.

**Reason:** The alternative was rerunning the station from step 1 with the answer added to the prompt, which keeps the prompt simpler. It lost because the stations' early steps assume a clean start. `unit-test-ticket` stops with "the fold already ran" once the acceptance file is gone, and `refactor-ticket` would reach step 3 again on a branch already carrying its `Fix #<N>` commit. A rerun hits guards written for a first run.

**Consequence:** The halt block every station subagent returns has to carry the step it stopped at, and the wrapper in `kanban/tdd-ticket/subagent-prompt.md` has to pass the step, the commits, and the answer back in. A station whose steps get renumbered or merged can break a resume, so a change to a station's step structure means checking how `tdd-ticket` resumes it.

**Scope:** `kanban/tdd-ticket/`

**Date:** 2026-11-26
