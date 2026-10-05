# Custom-skills

My skills for Claude Code and Antigravity (agy). What each skill does and how they fit together is on the [tutorial page](https://maxastrand04.github.io/Custom-skills/). This file only covers setup.

## Claude Code, from the marketplace

The quickest route. Inside Claude Code:

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

You get the kanban chain, the developer tools, and the behaviour skills, 15 in all. Run `/plugin marketplace update custom-skills` to pick up changes, and `/plugin uninstall max@custom-skills` to remove it.

## Claude Code or Antigravity, with install.sh

Use this for Antigravity, or if you want skills without the prefix. It symlinks each skill into `~/.claude/skills/` or `~/.gemini/config/skills/`, so the clone has to stay where you put it.

```bash
git clone https://github.com/Maxastrand04/Custom-skills.git ~/GitHub/Custom-skills
```

```bash
cd ~/GitHub/Custom-skills && ./install.sh
```

The menu asks for Claude Code, Antigravity, or both, then lets you tick skills. Already-installed skills start ticked. It prints a plan before changing anything and only removes links that point into this repo. With `fzf` on your PATH, tab toggles a skill and enter applies. Without it, type numbers, a category name, `all`, or `none`.

Skill names on the command line skip the menu and only add:

```bash
./install.sh grilling unslop
```

```bash
./install.sh --agy grilling
```

Restart the agent afterwards. In Claude Code check with `/skills`. In Antigravity type the skill name as a slash command.

`git pull` updates installed skills. Re-run `install.sh` only for new ones. To remove every link into this repo:

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
