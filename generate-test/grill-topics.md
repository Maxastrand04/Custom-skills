# Grill Topics

The Case Grill runs as Stage 4 of the `generate-test` orchestration loop. It populates the `cases` field of each agent block across all approved test files.

**Sequencing pin:** The grill does NOT begin until the user has explicitly approved the Structure preview with "approve" or "looks good, continue". Silence is not approval.

---

## Overview

The grill runs three named rounds. Rounds run in this order:

1. **Behavior** — cross-file
2. **Integration** — cross-file
3. **Unit** — per-file

Each round asks the user for cases. The skill asks; the user answers. Cases are always user-sourced. The skill never generates, infers, or proposes cases on behalf of the user. It may ask clarifying questions and use follow-up prompts to draw out the user's intent, but it never writes a case the user did not confirm.

At the end of all three rounds the skill presents the Cases preview (Stage 5). Nothing is written before that approval.

---

## Round 1 — Behavior (cross-file)

**Scope:** All approved test files that carry the `behavior` agent job.

**Purpose:** Surface the end-to-end and user-facing behaviors that cut across the whole system. These cases are gathered once, in a single cross-file conversation, rather than file-by-file — because behavioral paths often span multiple modules and it is easier for the user to think about them holistically.

**How it runs:**

1. The skill lists all test files assigned the `behavior` job and shows their source targets so the user has context.
2. The skill asks the user to describe the user-facing or end-to-end behaviors they want tested. Prompt example:

   > What are the key user-facing behaviors or end-to-end paths you want covered across these files? Describe each one in plain language.

3. For each behavior the user names, the skill confirms which test file it belongs to and records it as a case under that file's `behavior` agent block.
4. The skill continues asking follow-up questions (e.g. "Are there error paths or edge cases in this flow?") until the user signals they are done with this round (e.g. "done", "next", "move on").

**Output:** The `behavior` agent block in each relevant test file is populated with the user's confirmed cases.

---

## Round 2 — Integration (cross-file)

**Scope:** All approved test files that carry the `integration` agent job.

**Purpose:** Surface cases that cross module or system boundaries — database calls, HTTP requests, file I/O, multi-module chains. Gathered cross-file because integration paths often involve several modules talking to each other.

**How it runs:**

1. The skill lists all test files assigned the `integration` job and shows their source targets.
2. The skill asks the user to describe the cross-boundary interactions they want tested. Prompt example:

   > What cross-boundary interactions should be tested here — e.g. database reads/writes, external HTTP calls, file I/O, or chains across multiple modules? Describe each.

3. For each interaction the user names, the skill confirms which test file it belongs to and records it as a case under that file's `integration` agent block.
4. The skill continues asking follow-up questions (e.g. "Are there failure modes for this call — timeouts, bad responses, missing records?") until the user signals they are done with this round.

**Output:** The `integration` agent block in each relevant test file is populated with the user's confirmed cases.

---

## Round 3 — Unit (per-file)

**Scope:** All approved test files that carry the `unit` agent job.

**Purpose:** Surface isolated, symbol-level cases for individual functions, classes, or methods. Because unit cases are tightly bound to a specific source file, this round runs per-file: one file at a time in the order they appear in the approved structure.

**How it runs:**

1. The skill picks the first test file with a `unit` agent block.
2. It shows the file's source path and the symbols extracted during exploration.
3. It asks the user to supply cases for those symbols. Prompt example:

   > For `<source-file>` — what unit cases do you want for these symbols: `<symbol-list>`? Describe each case.

4. The user provides cases. The skill records each confirmed case under the file's `unit` agent block.
5. The skill asks follow-up questions per symbol as needed (e.g. "Any edge cases — empty input, null, boundary values?").
6. When the user is done with this file, the skill moves to the next file with a pending `unit` block and repeats.

**Deferral:** At any point in Round 3, the user may defer a file by saying "skip" or "defer". When deferred, the skill writes `cases: pending` for that file's `unit` block. A `pending` block is a valid placeholder; it must be revisited before agents run. Agents must not generate tests for `pending` blocks.

**Output:** The `unit` agent block in each relevant test file is either populated with the user's confirmed cases or marked `cases: pending`.

---

## Approval phrases

The only accepted approval phrases are:

- `approve`
- `looks good, continue`

These phrases gate the Structure preview (before the grill begins) and the Cases preview (after the grill ends). No other phrasing is treated as approval. Silence, "ok", "sure", or similar non-committal responses do not advance the workflow.

---

## Cases preview

After all three rounds complete, the skill presents the Cases preview: the full case list per test file, grouped by agent block, with each case's one-line description. The skill halts and waits for explicit approval before writing any file. The user may add, remove, or rename cases at this stage.
