#!/usr/bin/env python3
"""Build the max Plugin as an Antigravity plugin tree, and check one. No extra packages."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ".claude-plugin/marketplace.json"
RULES = "config/agy/AGENTS.md"
BUILD = ".agy-build"

# The tree's plugin.json holds these keys, in this order, and no others.
# version is filled in per build.
NAME = "max"
DISPLAY_NAME = "Max Åstrand's skills"
DESCRIPTION = "Ticket workflows, developer tools, and writing rules for Antigravity."


def build_tree(version, destination, root=ROOT):
    """Write the max Plugin for Antigravity into destination and return its skill names.

    version is the "X.Y.Z" the Release planned. destination is the folder the
    tree goes in, replaced whole when it already exists, so it holds this build
    and nothing older. root is the Custom-skills checkout to read from.

    The skills are the max entry's "skills" list in root/.claude-plugin/marketplace.json,
    in that order. Each listed folder lands at destination/skills/<folder name>/
    with every file under it, minus any whose path has a part starting with ".",
    and its Category folder dropped. File bytes are copied unchanged.
    root/config/agy/AGENTS.md is copied unchanged to destination/AGENTS.md.
    The manifest goes to destination/plugin.json as a JSON object with exactly
    the keys "name" (NAME), "version" (version), "displayName" (DISPLAY_NAME)
    and "description" (DESCRIPTION), in that order, indented two spaces, UTF-8
    with non-ASCII characters kept as written, ending in a newline. Nothing
    else is written, so nothing from config/agy/hooks/ or config/agy/hooks.json
    reaches the tree.

    Returns the skill folder names written, in marketplace order.

    Raises ValueError when version is not "X.Y.Z", when the catalog lacks
    exactly one max entry with a list of skill paths, when a listed skill
    folder does not exist, when two listed folders share a name, or when
    config/agy/AGENTS.md is missing. Every one of these is found before
    anything is written, so a ValueError leaves destination as it was.
    """
    raise NotImplementedError


def check_tree(tree):
    """Return every Antigravity rule the plugin tree at tree breaks, as messages.

    An empty list means the tree passes. Each message names the file or folder
    it is about, relative to tree, and the rule it breaks. Manifest problems
    come first, then skill problems ordered by skill folder name.

    The rules:
    - tree/plugin.json exists and holds a JSON object.
    - Its "name" exists and is lowercase kebab-case, ^[a-z0-9]+(-[a-z0-9]+)*$.
    - It has no key outside Antigravity's schema: "$schema", "name",
      "version", "displayName", "description", "skills", "disabled",
      "author", "homepage", "repository", "license", "keywords", "logo",
      "suggestedPrompts".
    - tree/skills/ holds at least one folder.
    - Every folder in tree/skills/ is named in lowercase kebab-case and holds
      a SKILL.md.
    - That SKILL.md opens with a frontmatter block, a "---" first line through
      the next "---" line.
    - The frontmatter has a "name: <value>" line whose value equals the
      folder name.
    - The frontmatter has a "description:" line with a value, or with ">" or
      "|" (plus an optional "-" or "+") followed by at least one indented
      line that is not blank.

    One message per broken rule, so a skill missing both name and description
    yields two. A rule that depends on a missing file is not reported on top
    of the missing file: no plugin.json yields one manifest message, and a
    folder with no SKILL.md, or a SKILL.md with no frontmatter, yields one
    message for that skill. Reads only; never changes the tree.

    Raises ValueError when tree is not an existing folder.
    """
    raise NotImplementedError


def main():
    """Command line for the release workflow.

    build VERSION   write the tree for VERSION into .agy-build/ at the repo root
                    and print how many skills it holds
    check           check .agy-build/ with check_tree; print each message on
                    its own line to stderr and exit 1 if there are any,
                    otherwise print how many skills passed

    Any ValueError prints "error: <reason>" and exits 1.
    """
    raise NotImplementedError


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
