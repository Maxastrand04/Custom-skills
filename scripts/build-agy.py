#!/usr/bin/env python3
"""Build the max Plugin as an Antigravity plugin tree, and check one. No extra packages."""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ".claude-plugin/marketplace.json"
RULES = "config/agy/AGENTS.md"
BUILD = ".agy-build"
MANIFEST = "plugin.json"
SKILLS = "skills"

NAME = "max"
DISPLAY_NAME = "Max Åstrand's skills"
DESCRIPTION = "Ticket workflows, developer tools, and writing rules for Antigravity."

VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
KEBAB = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
BLOCK_SCALAR = re.compile(r"[>|][-+]?")
SCHEMA_KEYS = {
    "$schema", "name", "version", "displayName", "description", "skills", "disabled",
    "author", "homepage", "repository", "license", "keywords", "logo", "suggestedPrompts",
}
USAGE = "usage: build-agy.py build VERSION | build-agy.py check"


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
    if not VERSION.fullmatch(version):
        raise ValueError(f"Version must be X.Y.Z, not {version!r}")
    folders = _listed_folders(root)
    rules = root / RULES
    if not rules.is_file():
        raise ValueError(f"Missing {RULES}")

    files = _tree_files(version, folders, rules)
    _replace_tree(Path(destination), files)
    return [folder.name for folder in folders]


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
    tree = Path(tree)
    if not tree.is_dir():
        raise ValueError(f"No tree at {tree}")
    messages = _manifest_problems(tree / MANIFEST)
    folders = _skill_folders(tree)
    if not folders:
        messages.append(f"{SKILLS}/: must hold at least one skill folder")
    for folder in folders:
        messages += _skill_problems(folder)
    return messages


def _listed_folders(root):
    """The max entry's skill folders, in marketplace order, each checked to exist."""
    path = root / CATALOG
    if not path.is_file():
        raise ValueError(f"Missing {CATALOG}")
    catalog = json.loads(path.read_text(encoding="utf-8"))
    plugins = catalog.get("plugins") if isinstance(catalog, dict) else None
    if not isinstance(plugins, list):
        raise ValueError(f"{CATALOG} has no plugins list")
    entries = [p for p in plugins if isinstance(p, dict) and p.get("name") == NAME]
    if len(entries) != 1:
        raise ValueError(f"{CATALOG} must have exactly one {NAME} entry, found {len(entries)}")
    skills = entries[0].get("skills")
    if not isinstance(skills, list) or not all(isinstance(s, str) for s in skills):
        raise ValueError(f"The {NAME} entry needs a list of skill paths")

    folders = {}
    for skill in skills:
        folder = root / skill
        if not folder.is_dir():
            raise ValueError(f"Listed skill folder does not exist: {skill}")
        if folder.name in folders:
            raise ValueError(f"Two listed skill folders are named {folder.name}")
        folders[folder.name] = folder
    return list(folders.values())


def _tree_files(version, folders, rules):
    """Every file the tree holds, as tree-relative path to bytes."""
    files = {"AGENTS.md": rules.read_bytes()}
    for folder in folders:
        for relative in _skill_files(folder):
            files[f"{SKILLS}/{folder.name}/{relative.as_posix()}"] = (folder / relative).read_bytes()
    manifest = {"name": NAME, "version": version, "displayName": DISPLAY_NAME, "description": DESCRIPTION}
    files[MANIFEST] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return files


def _skill_files(folder):
    """Paths of the files under folder, relative to it, sorted, minus any with a part starting with "."."""
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if path.is_file() and not any(part.startswith(".") for part in relative.parts):
            yield relative


def _replace_tree(destination, files):
    if destination.exists():
        shutil.rmtree(destination)
    for name, content in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def _manifest_problems(path):
    if not path.is_file():
        return [f"{MANIFEST}: missing"]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        manifest = None
    if not isinstance(manifest, dict):
        return [f"{MANIFEST}: must hold a JSON object"]

    messages = []
    name = manifest.get("name")
    if not isinstance(name, str) or not KEBAB.fullmatch(name):
        messages.append(f"{MANIFEST}: name must be lowercase kebab-case")
    unknown = sorted(set(manifest) - SCHEMA_KEYS)
    if unknown:
        messages.append(f"{MANIFEST}: keys outside Antigravity's schema: {', '.join(unknown)}")
    return messages


def _skill_folders(tree):
    return sorted((p for p in (tree / SKILLS).glob("*") if p.is_dir()), key=lambda p: p.name)


def _skill_problems(folder):
    where = f"{SKILLS}/{folder.name}"
    skill_md = f"{where}/SKILL.md"
    path = folder / "SKILL.md"
    if not path.is_file():
        return [f"{where}: missing SKILL.md"]
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    markers = [i for i, line in enumerate(lines) if line.rstrip() == "---"]
    if len(markers) < 2 or markers[0] != 0:
        return [f"{skill_md}: must open with a frontmatter block between --- lines"]
    settings = lines[1:markers[1]]

    messages = []
    if not KEBAB.fullmatch(folder.name):
        messages.append(f"{where}: folder name must be lowercase kebab-case")
    names = [line.removeprefix("name: ").strip() for line in settings if line.startswith("name: ")]
    if names != [folder.name]:
        messages.append(f"{skill_md}: frontmatter name must equal the folder name")
    if not _has_description(settings):
        messages.append(f"{skill_md}: frontmatter needs a description")
    return messages


def _has_description(settings):
    for index, line in enumerate(settings):
        if not line.startswith("description:"):
            continue
        value = line.removeprefix("description:").strip()
        if not BLOCK_SCALAR.fullmatch(value):
            return bool(value)
        for below in settings[index + 1:]:
            if below.strip():
                return below[0].isspace()
        return False
    return False


def main():
    """Command line for the release workflow.

    build VERSION   write the tree for VERSION into .agy-build/ at the repo root
                    and print how many skills it holds
    check           check .agy-build/ with check_tree; print each message on
                    its own line to stderr and exit 1 if there are any,
                    otherwise print how many skills passed

    Any ValueError or OSError prints "error: <reason>" and exits 1.
    """
    args = sys.argv[1:]
    tree = ROOT / BUILD
    if len(args) == 2 and args[0] == "build":
        names = build_tree(args[1], tree)
        print(f"Built {len(names)} skills into {BUILD}/")
    elif args == ["check"]:
        messages = check_tree(tree)
        if messages:
            print("\n".join(messages), file=sys.stderr)
            sys.exit(1)
        print(f"{len(_skill_folders(tree))} skills passed")
    else:
        raise ValueError(USAGE)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
