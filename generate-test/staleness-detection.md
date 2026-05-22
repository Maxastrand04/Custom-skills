# Staleness Detection

Owns bucket classification for Merge Re-run Mode. Every existing generated test file (identified by its frontmatter) is assigned to exactly one bucket. The bucket determines what action, if any, is permitted.

---

## Frontmatter contract

Every generated test file carries four frontmatter fields. These are the authoritative identifiers used for all comparisons in this file:

| Field | Meaning |
|---|---|
| `source` | Relative path to the source file under test |
| `test` | Relative path to this test file |
| `source_sha` | SHA of the source file at the time the test file was last written by the skill |
| `generated_sha` | SHA of the test file at the time the skill last wrote it |

No other field names are permitted. Any deviation from these exact names is a schema violation and must be flagged before classification proceeds.

---

## Bucket definitions

### Fresh

**Condition:** `source_sha` matches the current hash of the source file AND `generated_sha` matches the current hash of the test file.

**Meaning:** Neither the source nor the test file has changed since the skill last ran. Nothing to do.

**Action:** No action. Skip.

---

### Stale

**Condition:** `source_sha` does NOT match the current hash of the source file.

**Meaning:** The source file has changed since the test file was last written. The test file may no longer reflect the source's public surface.

**Action:** Structural-delta update (see Structural-delta update procedure below). Never full-regenerate.

---

### User-edited

**Condition:** `generated_sha` does NOT match the current hash of the test file — regardless of whether `source_sha` still matches.

**Meaning:** Someone has manually edited the test file since the skill last wrote it. The skill does not own this file's content anymore.

**Action:** Do NOT overwrite. Surface the file to the user with a warning. Only proceed if the user gives explicit per-change approval (see Individual accept/reject below).

---

### Orphan

**Condition:** The test file exists on disk but the path recorded in its `source` field no longer exists on disk.

**Meaning:** The source file was deleted or moved. The test file has no corresponding source.

**Action:** Do NOT delete the file. Surface it to the user. Wait for explicit instruction before taking any action. Never silently discard an orphan.

---

### New

**Condition:** A source file exists for which no corresponding generated test file is found (no test file with a matching `source` field in its frontmatter).

**Meaning:** The source file has not been covered by the skill yet.

**Action:** Run the normal orchestration loop (Stages 2–6 in SKILL.md) scoped to this source file.

---

## Detection algorithm

For each source file in scope and each existing generated test file, apply the following checks in order:

1. Read the test file's frontmatter. If fields are missing or misspelled, flag as a schema error and halt classification for that file.
2. Check whether the file at `source` path exists. If it does not exist → **Orphan**.
3. Compute the current hash of the source file. Compare to `source_sha`. If they differ → **Stale**.
4. Compute the current hash of the test file. Compare to `generated_sha`. If they differ → **User-edited**.
5. If all checks pass → **Fresh**.

For source files with no corresponding test file (no `source` field in any test file's frontmatter matches this source path) → **New**.

SHA comparison uses the full content hash of the file at the time of classification. Short git SHAs stored in frontmatter must be resolved to full content before comparison if the working tree is dirty.

---

## Structural-delta update procedure

Applies only to **Stale** files. Never applied to Fresh, User-edited, Orphan, or New files.

Goal: bring the test file's agent blocks in line with the current source file's surface without destroying user-added cases.

Steps:

1. Re-classify the source file using the exploration heuristics (`exploration-heuristics.md`) to get the current set of agents and targets.
2. Diff the current agent+target set against the agent blocks already in the test file:
   - **Added agents/targets:** agents or targets present in the current source but absent from the test file. Propose adding a new block (or extending an existing block's `**Targets:**` line).
   - **Removed agents/targets:** agents or targets present in the test file but no longer present in the source. Propose removing the block or target entry.
3. For each proposed change, present it individually and wait for explicit accept or reject before writing (see Individual accept/reject below).
4. Preserve all user-added cases in blocks that are not being removed.
5. When an agent block is being removed, do not delete its cases — carry them forward (see Orphaned cases carry-forward below).
6. After all accepted changes are written, recompute and update `source_sha` and `generated_sha` in the frontmatter.

Never perform a full regeneration of the test file. Only the diffed additions and removals are proposed.

---

## Orphaned cases carry-forward

When a structural-delta update removes an agent block (because the corresponding agent or symbol no longer exists in the source), its `**Cases:**` content must not be deleted.

Move those cases to a dedicated section at the bottom of the test file:

```
## Orphaned cases — needs decision

Cases from removed agent block `<job>` (targets: <targets>):
- <case 1>
- <case 2>
...
```

The user must explicitly decide what to do with these cases. They may:
- Reassign them to a different agent block.
- Delete them.
- Leave them in the orphaned section until a later pass.

The skill surfaces the orphaned section after delta application and asks the user for a decision. It does not auto-reassign or auto-delete cases.

---

## Individual accept/reject

No change proposed during a structural-delta update (or during any interaction with a User-edited file) may be applied in batch. Every change is presented individually:

- **What it is:** add block, remove block, add target, remove target, or modify frontmatter SHA.
- **What it will change:** show the before/after diff for that change only.
- **User response:** the user must say "accept" or "reject" for each change. Silence is not acceptance.

If the user rejects a change, it is not written and not re-proposed in the same session unless the user explicitly asks to revisit it.

Batch overrides such as "accept all" or "reject all" are not supported. Every change is individually gated.
