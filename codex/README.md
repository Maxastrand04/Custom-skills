# Codex packaging

The category folders hold the maintained skill sources. `scripts/build-codex.py` generates flat Codex copies without changing those sources.

Two outputs serve two installation routes:

| Route | Selection | Output |
|---|---|---|
| `install.sh --codex` | Every live skill is offered in the menu | `.codex-build/skills/`, ignored by git |
| Codex marketplace | The `max` plugin's `skills` in `.claude-plugin/marketplace.json` | `plugins/max/skills/`, tracked by git |

The builder removes Claude's `disable-model-invocation` setting from the Codex copies. Where that setting was true, it adds `agents/openai.yaml` with `policy.allow_implicit_invocation: false`. Behaviour skills keep Codex's default automatic selection. This follows [Codex's documented settings](https://learn.chatgpt.com/docs/build-skills).

Skill mentions change to Codex's `$skill-name` syntax for the personal installer and `$max:skill-name` for the marketplace. Relative links to shared files resolve between the flat folders. If a selected skill needs a file from an excluded skill, the builder includes that file and any shared files it needs, without including the excluded skill's `SKILL.md`. Removing a skill from the list therefore removes its availability, while a referenced shared file may remain.

The builder also replaces em dashes and curly quotes in the generated Markdown. It does not rewrite the workflows. Do not edit generated files by hand. Change the source or selection list, and GitHub Actions rebuilds the marketplace output. You can also build and commit it locally. Re-run the personal installer after source changes.

## Checks

```bash
python3 scripts/build-codex.py --check
python3 -m unittest discover -s tests -v
bash -n install.sh
```

The build check rejects stale output and unexpected files in the generated folders. GitHub Actions builds first, then runs these checks on every commit to the default branch and on pull requests that touch the Codex package, its sources, or the installer. Pull request runs validate the rebuilt output without pushing. Successful default-branch runs commit changes under `plugins/max/skills/` with the repository's built-in GitHub token. If the built skills differ from the commit that last set the version in `plugins/max/plugin.json`, the run also raises the version's last number in the same commit. The publish job needs permission to push to that branch. It skips a commit when the output is unchanged or a newer commit has reached the branch.

The built-in token's pushes do not trigger another push workflow, so the generated commit does not start a build loop. [GitHub token documentation](https://docs.github.com/en/actions/concepts/security/github_token)

## Proposed workflow edits

These are review findings, separate from the packaging changes applied here.

### PDF reading in schoolwork

`lecture-notes`, `lecture-preview`, and `write-formula-sheet` name Claude's Read tool and its page limit. `course-index` assumes the same limit. Codex can read PDFs through different tools, so that tool-specific wording should change to:

> Get the PDF's page count. Use the available PDF tools to read every page, in batches that fit their limits. Inspect page images where text extraction loses formulas or diagrams. Track the pages read and stop only when the last page is covered.

Keep each skill's existing scope and completion checks.

### Delegation in grilling and prune-skill

`grilling` requires fact-finding subagents. Some Codex sessions do not provide them, and `map-epic` requires work in the main conversation. Replace the unconditional delegation sentence with:

> Find facts yourself. Delegate independent checks only when subagents are available and the active workflow allows them. Otherwise investigate in the main conversation before asking questions that depend on the results.

`prune-skill` relies on two independent reads. Preserve that requirement and add:

> If independent subagents are unavailable or prohibited, report that the independent-read checks cannot run. Offer the findings as an unvalidated proposal. Do not claim the pruning has passed.

### External skill handoffs

`brainstorming` and `map-epic` mention `grill-with-docs`; `map-epic` also mentions `prototype`. Those skills are not supplied by this repo. Describe the work to do when the named skill is unavailable, or make that optional dependency clear. Packaging does not silently add external skills.

### Formula output

`write-formula-sheet` has examples with inline math that conflict with `science-output`'s format rules. Invoke `science-output` for both output files, rewrite the examples to its block format, and run its file check after writing. This is a consistency issue for both agents.

### Personal glossary

`gloss-me` reads `~/.claude/glossary.md`. The path can stay if both agents intentionally share your existing file. A reusable version should accept a user-specified glossary path and treat a missing file as empty. Codex may need approval to update a glossary outside its writable folders.

### Claude automation

`ci/` invokes Claude, selects Claude models, and uses Claude authentication. Converting that runner to Codex is separate work. Its skill names also overlap the interactive ticket skills, so it is excluded from both Codex outputs.

The setup has been checked for structure and packaging. The individual workflows still need real use in Codex to verify their behavior.
