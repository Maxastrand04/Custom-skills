# Custom-skills

My skills for Claude Code, Antigravity, and Codex. What each skill does and how they fit together is on the [tutorial page](https://maxastrand04.github.io/Custom-skills/). This file covers setup. The [setup page](https://maxastrand04.github.io/Custom-skills/setup.html) is a click-through version for Claude Code, Codex, and Antigravity.

> **Added a marketplace before releases existed?** You're reading from plain `main`, which stops working as a marketplace soon. Re-add it from the `release` branch once, as shown in [Re-adding a marketplace](#re-adding-a-marketplace).

## Codex, from your clone

Use `install.sh` for your personal selection. It offers every live skill, including schoolwork:

```bash
./install.sh --codex
```

Pick skills in the menu, review the plan, and apply it. To add specific skills without the menu:

```bash
./install.sh --codex grilling unslop gloss-me
```

Codex reads the links in `~/.agents/skills/`. Those links point to Codex copies generated inside this clone. The copies use Codex's invocation settings and `$skill-name` mentions, and put the skill folders beside one another so shared-file links resolve. Source files remain in their category folders. Python 3.9 or newer is required.

After editing a source skill or pulling updates, run `./install.sh --codex` again to refresh the copies. Codex detects changes automatically. Restart it if a skill does not appear. Use `/skills` or mention a skill as `$grilling` in Codex CLI and the editor extension. [Official skill documentation](https://learn.chatgpt.com/docs/build-skills)

Without a target flag, the script installs to Claude Code. Use `--codex` to select Codex, or combine target flags. `CUSTOM_SKILLS_CODEX_DIR` can override the Codex destination.

## Codex, from the marketplace

The Codex marketplace ships the same skills as the Claude marketplace. That covers the full ticket chain, the shared developer tools, and the writing and interview rules. Schoolwork, `prune-skill`, `show-me`, and `kanban-ci` are excluded.

Add the marketplace from the `release` branch, which only moves when a release goes out:

```bash
codex plugin marketplace add Maxastrand04/Custom-skills --ref release
codex plugin add max@custom-skills-codex
```

For local testing before pushing, replace the first command with `codex plugin marketplace add /absolute/path/to/Custom-skills`.

Marketplace skills have the `max:` prefix. Mention `$max:grilling`, for example, or select the skill in Codex's skill picker.

Install one Codex route per machine to avoid duplicate skills. Marketplace installs are cached copies. After a release, run `codex plugin marketplace upgrade custom-skills-codex`, then `codex plugin add max@custom-skills-codex` to refresh the installed package. [Official plugin documentation](https://developers.openai.com/plugins/build/plugins)

Both marketplaces read one list, the `skills` array of the `max` plugin in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json). To change it, edit that array, then run:

```bash
python3 scripts/build-codex.py
python3 scripts/build-codex.py --check
```

GitHub Actions rebuilds the package when the list or skill sources change. It validates pull requests and, on the default branch, commits updated `plugins/max/skills/` files automatically as a `chore` commit. You can still build and commit them locally. That build never touches the version. Only a release sets it, see [Releases](#releases). The personal installer always offers every live skill, independently of this list.

Packaging details and remaining proposed skill edits are in [codex/README.md](codex/README.md).

## Claude Code, from the marketplace (recommended)

The main way to install, and the quickest. Inside Claude Code:

```
/plugin marketplace add Maxastrand04/Custom-skills#release
/plugin install max@custom-skills
```

Or from a shell:

```bash
claude plugin marketplace add Maxastrand04/Custom-skills#release
```

```bash
claude plugin install max@custom-skills
```

Restart Claude Code or run `/reload-plugins`. Every skill carries the `max:` prefix, so you type `/max:grilling` or `/max:map-epic`. The tutorial writes them without the prefix.

You get the kanban chain, the developer tools, and the behaviour skills, 19 in all. Run `/plugin marketplace update custom-skills` to pick up a new release, and `/plugin uninstall max@custom-skills` to remove it.

## Releases

Both marketplaces serve the `release` branch, not `main`. Work merged to `main` reaches marketplace users only when I release it.

A release is a hand-started run of the **Release** workflow in the Actions tab, on `main`. Leave **dry run** ticked to see the version it would release and the commits that decided it. Untick it to release. The run builds the Codex package and runs the tests, then picks the next version from the conventional commits since the last `vX.Y.Z` tag. A breaking change (`feat!:` or a `BREAKING CHANGE:` body line) raises the first number, `feat` raises the middle, and `fix` raises the last. Other types and commits without a type raise nothing, and a release with none of the three stops without changing anything. The first release is `1.0.0`.

The run writes that one version into `max` on Claude, `max` on Codex, and `kanban-ci`, commits it to `main` as `chore(release): vX.Y.Z`, moves `release` forward to that commit, and creates the GitHub release page with notes grouped into breaking changes, features, and fixes. If a run fails partway, start it again and it finishes the same version. To try the version rules locally, run `python3 scripts/release.py plan`.

### Re-adding a marketplace

If you added a marketplace before releases existed, it points at `main`. Re-add it once from `release`.

Claude Code:

```bash
claude plugin marketplace remove custom-skills
claude plugin marketplace add Maxastrand04/Custom-skills#release
claude plugin install max@custom-skills
```

Codex:

```bash
codex plugin marketplace remove custom-skills-codex
codex plugin marketplace add Maxastrand04/Custom-skills --ref release
codex plugin add max@custom-skills-codex
```

## install.sh, step by step

Use this route if you want to change the skills, add your own, use Antigravity, or type skills without the `max:` prefix. The script symlinks each skill folder into `~/.claude/skills/` (Claude Code) or `~/.gemini/config/skills/` (Antigravity), so the agent reads straight from your clone and an edit to a `SKILL.md` applies the next time that skill runs.

If you installed from the marketplace, run `/plugin uninstall max@custom-skills` first. Otherwise every skill shows up twice.

**1. Fork the repo.** Click Fork on GitHub. Your fork is where your own changes live. If you only want my skills unchanged, you can skip the fork and clone `Maxastrand04/Custom-skills` directly.

**2. Clone it somewhere permanent.** The links point back into the clone, so moving or deleting the folder later breaks every installed skill.

```bash
git clone https://github.com/<you>/Custom-skills.git ~/GitHub/Custom-skills
```

**3. Run the installer.**

```bash
cd ~/GitHub/Custom-skills && ./install.sh
```

It asks which agent first:

```
Which agent?
  1) Claude Code    (~/.claude/skills)
  2) Antigravity    (~/.gemini/config/skills)
  3) Codex          (~/.agents/skills)
```

Pick one agent per run. Run the script again to set up another.

Then it lists every skill by category, with installed ones ticked. Type a number or a category name to toggle, `all` or `none` to set everything, and press enter to apply. With `fzf` on your PATH you get a picker instead, where tab toggles and enter applies. The list has a few more skills than the plugin, the `schoolwork/` ones among them.

Before changing anything it prints a plan and asks:

```
Plan for Claude Code (~/.claude/skills):
  + grilling
  + map-epic
  − old-skill  (stale: archived)
Apply? [y/N]
```

Unticked skills get unlinked. The script only ever removes links that point into this repo, so skills from anywhere else are safe.

**4. Restart the agent.** In Claude Code, check with `/skills`. In Antigravity, type a skill name as a slash command, such as `/grilling`.

### Without the menu

Skill names on the command line skip the menu and only add, never remove. `--claude`, `--agy`, and `--codex` pick the agent. Without a flag it installs to Claude Code only.

```bash
./install.sh grilling unslop
```

```bash
./install.sh --agy grilling
```

### Making it your own

- To edit a skill, change its `SKILL.md` and commit to your fork. No reinstall needed.
- To add a skill, create a folder with a `SKILL.md` inside `kanban/`, `developer-tools/`, `behaviour/`, or `schoolwork/` and run `./install.sh <name>`. The frontmatter needs a `name` that matches the folder and a `description`, and names must be unique across folders.
- To remove one of mine, untick it in the menu, or delete the folder and run `./install.sh` to clear the leftover link.

### Getting my updates

`git pull` updates the skills you already have. For a fork, add this repo as `upstream` once, then merge from it when you want my changes:

```bash
git remote add upstream https://github.com/Maxastrand04/Custom-skills.git
```

```bash
git pull upstream main
```

Run `./install.sh` again only when a pull brings in a new skill you want.

### Removing everything

Untick everything in the menu, or remove every link into the repo by hand:

```bash
find ~/.claude/skills ~/.gemini/config/skills -maxdepth 1 -type l -exec sh -c 'readlink "$1" | grep -q "/Custom-skills/" && rm "$1"' _ {} \;
```

## What's in the repo

```
kanban/            the ticket workflow
developer-tools/   coding and explanation skills used as needed
behaviour/         wording and interview rules other skills borrow
schoolwork/        study skills, install.sh only
archive/           retired, never installed
config/            my settings, hooks, and instruction files, reference only
```

Each folder's README lists its skills. Design decisions are in [`docs/adr/`](docs/adr/), and [`CONTEXT.md`](CONTEXT.md) defines the terms the skills use.
