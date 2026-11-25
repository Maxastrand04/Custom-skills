# Research: How Antigravity installs a plugin from a GitHub repo

Answers for [issue #70](https://github.com/Maxastrand04/Custom-skills/issues/70), supporting [epic #69](https://github.com/Maxastrand04/Custom-skills/issues/69).

Checked on 2026-11-25 against the official Antigravity documentation (`antigravity.google/docs/`), the built-in `agy-customizations` skill docs, and live tests with `agy 1.5.17`.

## 1. Repository layout and manifest

Antigravity reads a repository as a plugin when the repo root contains a `plugin.json` manifest alongside component directories. For multi-tool repos that also ship `.claude-plugin/plugin.json` or `.cursor-plugin/plugin.json`, `.antigravity-plugin/plugin.json` works too and takes precedence over a root `plugin.json`. For a dedicated repo like `Custom-skills-agy`, a root `plugin.json` is the standard layout.

```text
Custom-skills-agy/
├── plugin.json
├── README.md
├── rules/                 # Optional: rules/AGENTS.md (root AGENTS.md is ignored in plugins)
├── hooks.json             # Optional: must sit at repo root, not hooks/hooks.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md       # Required: frontmatter name must match <skill-name>
        ├── scripts/       # Optional
        ├── references/    # Optional
        └── assets/        # Optional
```

Antigravity scans `skills/` one level deep. It skips category subfolders like `skills/behaviour/unslop/SKILL.md` unless you declare extra directories in `plugin.json`'s `skills` field. Flattening the `max` skills directly under `skills/<skill-name>/SKILL.md` avoids extra config.

### Manifest fields (`plugin.json`)

The schema at `https://antigravity.google/schemas/v1/plugin.json` sets `"additionalProperties": false`, so unknown keys fail validation.

| Field | Required for GitHub install | Notes |
| --- | --- | --- |
| `name` | Yes | Lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`). Required by `agy plugin install` and `agy plugin validate --strict`. |
| `$schema` | No | `"https://antigravity.google/schemas/v1/plugin.json"` for editor validation. |
| `version` | No (Marketplace requires it) | Semver string like `"2.0.0"`. Shown in `agy plugin list`. |
| `displayName` | No (Marketplace requires it) | Human-readable title shown in plugin lists. |
| `description` | No (Marketplace requires it) | Short summary of the plugin. |
| `skills` | No | Extra relative skill directories loaded in addition to `skills/`. Omit when all skills live under `skills/`. |
| `disabled` | No | Defaults to `false`. |
| `author`, `homepage`, `repository`, `license`, `keywords`, `logo`, `suggestedPrompts` | No (Marketplace requires `author` and `logo`) | Optional metadata. Missing `logo` emits only an informational note in `agy plugin validate`, not a warning or error. |

Each `skills/<skill-name>/SKILL.md` requires YAML frontmatter with `name` (lowercase kebab-case matching its parent directory name) and `description`.

If `Custom-skills-agy` later ships `config/agy/` files, rules must go in `rules/AGENTS.md` (not a root `AGENTS.md`, which native plugins ignore) and hooks must go in a root `hooks.json` (not `hooks/hooks.json`). You can check the built tree in CI with `agy plugin validate --strict <dir>`.

**Sources.**
- [Build plugins (`antigravity.google/docs/build-plugins.md`)](https://antigravity.google/docs/build-plugins.md), sections "Directory structure", "Manifest file (`plugin.json`)", "Full JSON schema", "Authoring plugin components", and "Warnings in multi-tool repositories".
- [Customization discovery (`antigravity.google/docs/customization-discovery.md`)](https://antigravity.google/docs/customization-discovery.md), section "Scan depth".
- Built-in `agy-customizations` doc (`~/.gemini/antigravity-cli/builtin/skills/agy-customizations/docs/plugins.md`), section "Lifecycle Scoping".
- Verified with `agy plugin validate` on `agy 1.5.17` against a minimal local plugin.

## 2. How a user installs from `Maxastrand04/Custom-skills-agy`

The primary install path for a GitHub repo is the Antigravity CLI shell command:

```bash
agy plugin install https://github.com/Maxastrand04/Custom-skills-agy
```

That clones the repository and stages it into `~/.gemini/config/plugins/<plugin-name>/`. Both the Antigravity CLI and the Antigravity App read global plugins from `~/.gemini/config/plugins/`, so a plugin installed through the CLI shows up automatically in the App under **Customizations > Installed**.

There is no GitHub URL input in the Antigravity App UI or the interactive `/plugin` TUI panel. The App's **Customizations > Marketplace** tab only lists Google and partner Marketplace catalogs, and `/plugin install` only documents Marketplace identifiers and local paths. A user without the CLI can still install manually by cloning the repo directly into `~/.gemini/config/plugins/<plugin-name>/` (global) or `.agents/plugins/<plugin-name>/` (workspace).

**Sources.**
- [Plugins (`antigravity.google/docs/plugins.md`)](https://antigravity.google/docs/plugins.md), sections "Antigravity App", "Antigravity CLI", "CLI shell subcommands (`agy plugin`)", and "CLI filesystem location".
- [Marketplace (`antigravity.google/docs/marketplace.md`)](https://antigravity.google/docs/marketplace.md), section "Install from a GitHub link".
- [Agent skills (`antigravity.google/docs/skills.md`)](https://antigravity.google/docs/skills.md), section "Managing skills with plugins".

## 3. Pinning a branch or tag

Users can pin a branch or tag by passing a GitHub `/tree/<ref>` URL:

```bash
# Default branch
agy plugin install https://github.com/Maxastrand04/Custom-skills-agy

# Pinned tag or branch
agy plugin install https://github.com/Maxastrand04/Custom-skills-agy/tree/v2.0.0
```

`agy plugin validate --help` also documents subfolder targeting with `https://github.com/<owner>/<repo>/tree/<branch>/<path>`.

Other ref syntaxes do not work. Live checks on `agy 1.5.17` against `datadog-labs/antigravity-plugin` (which has tag `v0.1.2` and `main` at `v1.0.0`) showed:

- `.../tree/v0.1.2` installed version `0.1.2`.
- The bare repo URL installed version `1.0.0`.
- `...@v0.1.2` failed with `git clone` exit status 128 (`repository '...antigravity-plugin@v0.1.2.git/' not found`).
- `...#v0.1.2` ignored the fragment and cloned the default branch.

**Sources.**
- `agy plugin validate --help` (`agy 1.5.17`).
- Live CLI test with `agy plugin install` and `agy plugin list --json` (`agy 1.5.17`) against `https://github.com/datadog-labs/antigravity-plugin`.

## 4. Skill name prefixing and cross-skill references

Antigravity does not prefix plugin skill names at runtime. Bundled skills register under their bare `SKILL.md` name and run as `/<skill-name>`.

The official docs contradict each other on this point. `customization-discovery.md` says "Skills from a plugin are named `<plugin>:<skill>`, so they don't conflict with your other skills", while `plugins.md` and `build-plugins.md` show bare slash commands like `/hello` and `/dart-add-unit-test`, and `agy plugin list --json` lists bare skill names.

To settle the contradiction, I installed a test plugin (`test-agy-plugin`) containing `skills/alpha-skill/SKILL.md` and inspected the `Available skills` list injected into an `agy 1.5.17` session. The skill appeared unprefixed:

```text
- alpha-skill (/Users/max/.gemini/config/plugins/test-agy-plugin/skills/alpha-skill/SKILL.md): Temporary test skill for checking Antigravity plugin skill naming.
```

(Bundled MCP servers are a different case; Antigravity prefixes those as `<plugin-name>_<server-name>`.)

Because plugin skills keep their bare names, cross-skill references in `Custom-skills` (such as invoking `gloss-me`, `grill-docs`, `unslop`, or `/pr-ticket`) do not need any rewriting for Antigravity. One side effect to note for users migrating from `./install.sh --agy` is that bare plugin skill names can collide with loose symlinks in `~/.gemini/config/skills/`, where personal skills take precedence over plugins.

**Sources.**
- [Plugins (`antigravity.google/docs/plugins.md`)](https://antigravity.google/docs/plugins.md), sections "What a plugin bundles", "Starter prompts and skills", and `agy plugin list --json` example.
- [Build plugins (`antigravity.google/docs/build-plugins.md`)](https://antigravity.google/docs/build-plugins.md), section "Agent skills".
- [Customization discovery (`antigravity.google/docs/customization-discovery.md`)](https://antigravity.google/docs/customization-discovery.md), section "Which customization wins" (contains the conflicting `<plugin>:<skill>` claim).
- Live CLI test with `agy 1.5.17` (`agy --effort low -p ...` inspecting the active skill list).

## 5. Picking up a new version

A GitHub-installed plugin only picks up a new version when the user reinstalls it.

`agy plugin` has no `update` subcommand (`agy plugin update` exits with `Error: unknown command: update`). When `agy plugin install` installs from GitHub or a local folder, `~/.gemini/config/import_manifest.json` records only `name`, `"source": "antigravity"`, `importedAt`, and `components`. It does not store the GitHub URL or ref, so Antigravity cannot check for upstream updates automatically. (The `version` field note in `build-plugins.md` about clients detecting updates applies to Marketplace catalog plugins, not direct GitHub installs.)

Re-running the install command updates the plugin in place without needing `agy plugin uninstall` first:

```bash
agy plugin install https://github.com/Maxastrand04/Custom-skills-agy
```

Live testing on `agy 1.5.17` confirmed that re-running `agy plugin install` overwrites the existing directory and prints `(replaced existing installation)`. User enable/disable settings live in `~/.gemini/config/config.json` rather than inside the plugin folder, so preferences survive reinstalls.

Because `agy plugin install` clones the repository with its `.git` directory intact into `~/.gemini/config/plugins/<plugin-name>/`, running `git pull` inside that folder works for an unpinned branch, though it is undocumented. Documenting the re-run of `agy plugin install` is the cleaner instruction for users.

**Sources.**
- `agy plugin --help` and `agy plugin update` (`agy 1.5.17`).
- Inspected `~/.gemini/config/import_manifest.json` and `~/.gemini/config/plugins/<name>/` after GitHub and local installs (`agy 1.5.17`).
- Built-in `agy-customizations` doc (`~/.gemini/antigravity-cli/builtin/skills/agy-customizations/docs/plugins.md`), section "Turning Plugins On and Off".
- [Build plugins (`antigravity.google/docs/build-plugins.md`)](https://antigravity.google/docs/build-plugins.md), `version` field description.
