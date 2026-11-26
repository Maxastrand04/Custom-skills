#!/usr/bin/env python3
"""Build the max Plugin as an Antigravity plugin tree, and check one. No extra packages."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
USAGE = "usage: build-agy.py build VERSION [SOURCE] | build-agy.py check | build-agy.py publish VERSION REMOTE"
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


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


def publish_tree(version, tree, remote):
    """Push the plugin tree at tree to remote's default branch as Release version, and tag it.

    version is the "X.Y.Z" the Release planned. tree is a folder build_tree
    wrote for that version. remote is any URL git clone accepts: the
    workflow passes Custom-skills-agy's SSH URL, tests pass a local bare repo.

    Clones remote into a temporary folder, removed before returning
    whatever happens, and works only there; the Custom-skills checkout and
    tree are never changed. Then:

    - If remote already has the tag "vX.Y.Z", returns None and pushes
      nothing, so a re-run after a later step failed is safe.
    - Otherwise the clone's files become tree's files. Every tracked file
      not in tree is deleted, every file in tree is written with its bytes
      unchanged, and README.md at the clone root and everything under
      .github/ are left exactly as they were, even when tree has a file at
      the same path.
    - Commits that as "chore(release): vX.Y.Z", author and committer
      "github-actions[bot]" <41898282+github-actions[bot]@users.noreply.github.com>,
      even when no file changed, so every Release gets its commit. If the
      default branch's newest commit already has that title, because an
      earlier run pushed it and then failed to tag, it is reused instead of
      committing again.
    - Pushes the commit to the default branch without force, so a branch
      that moved ahead of the clone rejects the push.
    - Creates the lightweight tag "vX.Y.Z" on that commit and pushes it.
      The tag is pushed only after the commit push succeeds.

    Returns the full hash of the tagged commit, or None when the tag
    already existed.

    Raises ValueError when version is not "X.Y.Z", when tree is not an
    existing folder, or when tree/plugin.json is missing or its "version"
    is not version. Every one of these is found before remote is cloned.
    Raises RuntimeError when a git command fails, such as the clone, either
    push, or a remote with no default branch, naming the command and git's
    error output. A failed commit push leaves remote with no new commit and
    no tag.
    """
    tree = Path(tree)
    _check_publish_input(version, tree)
    tag = _tag_name(version)
    with tempfile.TemporaryDirectory(prefix="agy-publish-") as temp:
        clone = Path(temp) / "clone"
        _git(temp, "clone", "--quiet", "--", str(remote), str(clone))
        if _git(clone, "ls-remote", "--tags", "origin", f"refs/tags/{tag}"):
            return None
        branch = _default_branch(clone)
        title = f"chore(release): {tag}"
        if _git(clone, "log", "-1", "--format=%s") != title:
            _commit_and_push_tree(clone, tree, title, branch)
        commit = _git(clone, "rev-parse", "HEAD")
        _git(clone, "tag", tag, commit)
        _git(clone, "push", "--quiet", "origin", f"refs/tags/{tag}")
        return commit


def _tag_name(version):
    """The Release tag for an "X.Y.Z" version, "vX.Y.Z"."""
    return f"v{version}"


def _check_publish_input(version, tree):
    """Raise ValueError unless version is "X.Y.Z" and tree is a folder built for it."""
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError(f"Version must be X.Y.Z, got {version!r}")
    if not tree.is_dir():
        raise ValueError(f"Not a folder: {tree}")
    manifest_path = tree / MANIFEST
    if not manifest_path.is_file():
        raise ValueError(f"{tree} has no {MANIFEST}")
    manifest = _load_json(manifest_path)
    built_for = manifest.get("version") if isinstance(manifest, dict) else None
    if built_for != version:
        raise ValueError(f"{manifest_path} is for version {built_for!r}, not {version}")


def _default_branch(clone):
    """The clone's default branch name, or RuntimeError when it has no commit yet."""
    branch = _git(clone, "symbolic-ref", "--short", "HEAD")
    _git(clone, "rev-parse", "--verify", "HEAD")
    return branch


def _commit_and_push_tree(clone, tree, title, branch):
    """Make the clone hold tree's files, commit that as the Actions bot, and push it to branch."""
    _sync_clone(clone, tree)
    _git(clone, "add", "--all", "--force")
    _git(clone, "commit", "--quiet", "--allow-empty", "--no-verify", "-m", title, bot=True)
    _git(clone, "push", "--quiet", "origin", f"HEAD:refs/heads/{branch}")


def _kept(path):
    """True for a clone-relative posix path publish_tree never replaces."""
    return path == "README.md" or path.startswith(".github/")


def _sync_clone(clone, tree):
    """Make the clone's files tree's files, leaving the kept paths alone."""
    tracked = _git(clone, "ls-files", "-z", strip=False).split("\0")
    for path in filter(None, tracked):
        if not _kept(path):
            _delete_file(clone / path, clone)
    for source in sorted(tree.rglob("*")):
        relative = source.relative_to(tree).as_posix()
        if source.is_file() and not _kept(relative) and not relative.startswith(".git/"):
            _write_file(clone / relative, source.read_bytes())


def _delete_file(target, root):
    """Delete the file at target, then every folder under root that this leaves empty."""
    target.unlink(missing_ok=True)
    for folder in target.parents:
        if folder == root or not folder.is_dir() or any(folder.iterdir()):
            return
        folder.rmdir()


def _git(cwd, *args, bot=False, strip=True):
    """Run git in cwd and return its output, or raise RuntimeError naming the command."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    if bot:
        env.update(
            GIT_AUTHOR_NAME=BOT_NAME, GIT_AUTHOR_EMAIL=BOT_EMAIL,
            GIT_COMMITTER_NAME=BOT_NAME, GIT_COMMITTER_EMAIL=BOT_EMAIL,
        )
    command = ["git", *args]
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {output}")
    return result.stdout.strip() if strip else result.stdout


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
        _write_file(destination / name, content)


def _write_file(target, content):
    """Write content's bytes to target, making its parent folders first."""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)


def _manifest_problems(path):
    if not path.is_file():
        return [f"{MANIFEST}: missing"]
    manifest = _load_json(path)
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


def _load_json(path):
    """The JSON value in the UTF-8 file at path, or None when it isn't valid JSON."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


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

    build VERSION [SOURCE]
                    write the tree for VERSION into .agy-build/ at the repo root
                    and print how many skills it holds. The skills, their list
                    and the rules file are read from the checkout at SOURCE, or
                    from this repo when SOURCE is left out
    check           check .agy-build/ with check_tree; print each message on
                    its own line to stderr and exit 1 if there are any,
                    otherwise print how many skills passed
    publish VERSION REMOTE
                    publish .agy-build/ to REMOTE as VERSION with
                    publish_tree; print "Published vVERSION as <commit>"
                    when it pushed, or "vVERSION is already published,
                    nothing pushed" when the tag already existed. Exit 0
                    either way. REMOTE is any URL git clone accepts; the
                    workflow passes Custom-skills-agy's SSH URL.

    Any ValueError, OSError or RuntimeError prints "error: <reason>" and
    exits 1.
    """
    args = sys.argv[1:]
    tree = ROOT / BUILD
    if len(args) in (2, 3) and args[0] == "build":
        source = Path(args[2]) if len(args) == 3 else ROOT
        names = build_tree(args[1], tree, source)
        print(f"Built {len(names)} skills into {BUILD}/")
    elif args == ["check"]:
        messages = check_tree(tree)
        if messages:
            print("\n".join(messages), file=sys.stderr)
            sys.exit(1)
        print(f"{len(_skill_folders(tree))} skills passed")
    elif len(args) == 3 and args[0] == "publish":
        tag = _tag_name(args[1])
        commit = publish_tree(args[1], tree, args[2])
        if commit is None:
            print(f"{tag} is already published, nothing pushed")
        else:
            print(f"Published {tag} as {commit}")
    else:
        raise ValueError(USAGE)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
