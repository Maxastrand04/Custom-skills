# Custom-skills

My skills for Claude Code and Antigravity (agy). What each skill does and how they fit together is on the [tutorial page](https://maxastrand04.github.io/Custom-skills/). This file only covers setup. For a click-through version to send around, use the [setup page](https://maxastrand04.github.io/Custom-skills/setup.html).

## Claude Code, from the marketplace (recommended)

The main way to install, and the quickest. Inside Claude Code:

```
/plugin marketplace add Maxastrand04/Custom-skills
/plugin install max@custom-skills
```

Or from a shell:

```bash
claude plugin marketplace add Maxastrand04/Custom-skills
```

```bash
claude plugin install max@custom-skills
```

Restart Claude Code or run `/reload-plugins`. Every skill carries the `max:` prefix, so you type `/max:grilling` or `/max:map-epic`. The tutorial writes them without the prefix.

You get the kanban chain, the developer tools, and the behaviour skills, 16 in all. Run `/plugin marketplace update custom-skills` to pick up changes, and `/plugin uninstall max@custom-skills` to remove it.

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
  3) Both
```

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

Skill names on the command line skip the menu and only add, never remove. `--claude` and `--agy` pick one agent; without them it installs to both.

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
