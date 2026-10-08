#!/usr/bin/env python3
"""Build Codex skills from the maintained category folders. No extra packages."""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ("kanban", "developer-tools", "behaviour", "schoolwork")
SIBLING_FILE = re.compile(r"\.\./([a-z0-9-]+)/([a-zA-Z0-9_./-]+\.md)")


def live_skills():
    skills = {}
    for category in CATEGORIES:
        for path in sorted((ROOT / category).glob("*/SKILL.md")):
            name = path.parent.name
            if name in skills:
                raise ValueError(f"Duplicate skill name: {name}")
            text = path.read_text()
            if not re.match(r"\A---\n", text) or text.count("---") < 2:
                raise ValueError(f"Missing settings block: {path}")
            settings = text.split("---", 2)[1]
            if not re.search(rf"^name: {re.escape(name)}$", settings, re.M):
                raise ValueError(f"Name must match folder: {path}")
            if not re.search(r"^description: \S", settings, re.M):
                raise ValueError(f"Missing description: {path}")
            skills[name] = path.parent
    return skills


def convert(text, names, skill=False, prefix=""):
    if skill:
        _, settings, body = text.split("---", 2)
        settings = re.sub(r"^disable-model-invocation:.*\n", "", settings, flags=re.M)
        text = "---" + settings + "---" + body
    for name in sorted(names, key=len, reverse=True):
        text = re.sub(rf"(?<![\w./])/{re.escape(name)}(?![\w/-])", f"${prefix}{name}", text)
    return text.replace("—", ",").replace("“", '"').replace("”", '"').replace("’", "'")


def build_files(selected, skills, prefix=""):
    files = {}
    pending = []
    for name in selected:
        source = skills[name]
        for path in sorted(source.rglob("*")):
            if path.is_file():
                relative = path.relative_to(source)
                if any(part.startswith(".") for part in relative.parts):
                    continue
                pending.append((name, path, relative))
        settings = (source / "SKILL.md").read_text().split("---", 2)[1]
        if re.search(r"^disable-model-invocation: true$", settings, re.M):
            files[f"{name}/agents/openai.yaml"] = b"policy:\n  allow_implicit_invocation: false\n"

    seen = set()
    while pending:
        name, path, relative = pending.pop()
        key = f"{name}/{relative.as_posix()}"
        if key in seen:
            continue
        seen.add(key)
        if path.suffix == ".md":
            text = convert(path.read_text(), skills, relative.as_posix() == "SKILL.md", prefix)
            for owner, filename in SIBLING_FILE.findall(text):
                if owner not in skills or filename == "SKILL.md":
                    raise ValueError(f"Unsupported sibling reference in {path}: {owner}/{filename}")
                source = skills[owner] / filename
                if not source.is_file() or not source.resolve().is_relative_to(skills[owner].resolve()):
                    raise ValueError(f"Missing or escaping sibling file in {path}: {source}")
                pending.append((owner, source, Path(filename)))
            files[key] = text.encode()
        else:
            files[key] = path.read_bytes()
    return files


def sync(destination, files, check):
    manifest = destination / ".generated-files.json"
    previous = json.loads(manifest.read_text()) if manifest.exists() else []
    actual = {p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()}
    unmanaged = actual - set(previous) - {manifest.name}
    if unmanaged:
        raise ValueError(f"Unmanaged files in generated output: {', '.join(sorted(unmanaged))}")
    expected = dict(files)
    expected[manifest.name] = (json.dumps(sorted(files), indent=2) + "\n").encode()
    changed = []
    for key, content in expected.items():
        path = destination / key
        if not path.is_file() or path.read_bytes() != content:
            changed.append(key)
    stale = set(previous) - set(files)
    if check:
        if changed or stale:
            raise ValueError("Generated skills need rebuilding. Run python3 scripts/build-codex.py")
        return
    for key in previous:
        if not (destination / key).resolve().is_relative_to(destination.resolve()):
            raise ValueError(f"Generated file leaves output folder: {key}")
    for key in changed:
        path = destination / key
        if path.exists() and key not in previous and key != manifest.name:
            raise ValueError(f"Refusing to overwrite an unmanaged file: {path}")
    for key in stale:
        (destination / key).unlink(missing_ok=True)
    for key in changed:
        path = destination / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(expected[key])


def marketplace_entries():
    """The Codex marketplace ships the Claude plugin's skill list, so the two cannot differ."""
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    plugins = [p for p in marketplace.get("plugins", []) if p.get("name") == "max"]
    if len(plugins) != 1 or not isinstance(plugins[0].get("skills"), list):
        raise ValueError("Claude marketplace needs one max plugin with a skills list")
    entries = plugins[0]["skills"]
    if not all(isinstance(p, str) for p in entries):
        raise ValueError("Claude marketplace skills must be paths")
    return [p.removeprefix("./") for p in entries]


def bump_version(manifest):
    """Raise the last number of the plugin version so Codex installs a fresh copy."""
    text = manifest.read_text()
    match = re.search(r'"version": "(\d+)\.(\d+)\.(\d+)"', text)
    if not match:
        raise ValueError(f"No X.Y.Z version in {manifest}")
    major, minor, patch = match.groups()
    version = f"{major}.{minor}.{int(patch) + 1}"
    manifest.write_text(text[:match.start()] + f'"version": "{version}"' + text[match.end():])
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true", help="Build all live skills for install.sh")
    parser.add_argument("--check", action="store_true", help="Check generated files without writing")
    parser.add_argument("--bump-version", action="store_true", help="Raise the marketplace plugin version")
    args = parser.parse_args()
    if args.bump_version:
        print(f"Raised plugin version to {bump_version(ROOT / 'plugins' / 'max' / 'plugin.json')}")
        return
    skills = live_skills()
    if args.local:
        selected = list(skills)
        destination = ROOT / ".codex-build" / "skills"
    else:
        entries = marketplace_entries()
        selected = []
        for entry in entries:
            source = ROOT / entry
            if source not in skills.values():
                raise ValueError(f"Not a live skill: {entry}")
            if source.name in selected:
                raise ValueError(f"Repeated marketplace skill: {entry}")
            selected.append(source.name)
        destination = ROOT / "plugins" / "max" / "skills"
    sync(destination, build_files(selected, skills, "" if args.local else "max:"), args.check)
    action = "Checked" if args.check else "Built"
    print(f"{action} {len(selected)} Codex skills in {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
