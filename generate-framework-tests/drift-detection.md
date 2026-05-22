# Drift Detection

Governs the sidecar manifest, the fast-exit rule, drift analysis, user-added-case immunity, orphan handling, and manifest writes. Execute these rules on every invocation after scope is determined.

---

## Manifest path and schema

The manifest lives at `.generate-framework-tests/sidecar-manifest.json`, always relative to the project root. Its structure is:

```json
{
  "<source_path>": {
    "source_sha": "<sha256 hex of source file contents>",
    "generated_at": "<ISO 8601 timestamp>",
    "cases": ["<case_name_1>", "<case_name_2>"]
  }
}
```

- `source_path` is relative to the project root (e.g. `src/auth/login.py`).
- `cases` is the authoritative list of test case names the skill wrote for this source file. It records what the skill owns — nothing more.
- SHA-256 is computed over raw file bytes, not normalized content.

---

## Fast-exit rule

Execute this check at the very start of every invocation, immediately after scope is determined.

1. If the manifest file does not exist, proceed normally — no tests have been generated yet.
2. For every source file in scope, compute the SHA-256 of its current contents. Look up the `source_sha` for that file in the manifest.
3. Check whether any source file in scope has no manifest entry at all (new untested file).
4. If ALL of the following are true, print `all tests are up to date — nothing to do` and exit:
   - Every source file in scope has a manifest entry.
   - Every computed SHA-256 matches the `source_sha` in its manifest entry.
   - No source file in scope is missing a manifest entry.
5. If any condition above is false, proceed to drift analysis.

---

## Drift-diff algorithm

For each source file in scope whose SHA-256 differs from the manifest's `source_sha`:

1. Re-read the source file and re-derive a proposed case list using the same logic as initial generation.
2. Compare the proposed case list to the `cases[]` array stored in the manifest entry for that source file.
3. Classify each difference into one of three buckets:
   - `+add`: a case name is in the proposed list but not in `cases[]` — new behaviour appeared in the source that needs a test.
   - `-remove`: a case name is in `cases[]` but not in the proposed list — the corresponding source behaviour was removed.
   - `~update`: a case name appears in both the proposed list and `cases[]`, but the surrounding source context has changed enough to indicate the intent of that case has shifted (same name, different behaviour).
4. Include all three buckets in the files-to-update section of the approval plan presented to the user. No changes are written until the plan is approved.

For source files in scope with no manifest entry, treat them as new and run the normal generation path.

---

## User-added-case immunity

After the skill writes tests, a user may add their own test cases to a generated test file. These user-authored cases must never be touched.

**Identifying user-authored cases:** any test case name present in the test file but absent from the manifest's `cases[]` for that source file is user-authored.

Apply this rule at both drift-diff time and write time:

- At drift-diff time: exclude user-authored case names from all three diff buckets. Do not propose adding, removing, or updating them.
- At write time: when rewriting a test file, preserve every user-authored case verbatim. Never move, rename, reformat, or delete them.

This immunity is unconditional — it applies regardless of what changed in the source file.

---

## Orphan rule

An orphan is a manifest entry whose source file no longer exists on disk (the file was deleted or moved).

1. During scope scan, check every manifest entry: if the source file at `source_path` does not exist, mark that entry as an orphan.
2. Include each orphan in the approval plan with a removal proposal, for example:
   > `tests/foo/test_bar.py` — source `src/foo/bar.py` was deleted; propose removing test file.
3. Do not remove the test file or the manifest entry until the user explicitly confirms removal in the plan approval.
4. After confirmed removal: delete the test file, then delete the manifest entry for that source path.

Never silently discard an orphan.

---

## Manifest write rule

Only the skill writes the manifest. Users and other tools must not edit it.

Write the manifest after all test files for this invocation have been successfully written — never before.

For each source path that was written or updated in this invocation, overwrite its manifest entry entirely (not a merge). Record:
- `source_sha`: SHA-256 of the source file as it was read during this invocation.
- `generated_at`: current UTC time in ISO 8601 format.
- `cases`: the complete, up-to-date list of case names the skill wrote into the test file. This replaces the previous `cases[]` entirely.

For confirmed orphan removals, delete the manifest entry for that source path entirely.

If writing the manifest fails, report the error to the user but do not roll back the test files that were already written.
