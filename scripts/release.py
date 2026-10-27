#!/usr/bin/env python3
"""Pick the next release version from conventional commits and write it. No extra packages."""

import json
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ".claude-plugin/marketplace.json"
PLUGIN_MANIFESTS = ("plugins/max/plugin.json", "ci/.claude-plugin/plugin.json")
VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")
TAG = re.compile("v" + VERSION.pattern)
CONVENTIONAL = re.compile(r"([A-Za-z]+)(\([^)]*\))?(!)?:")
RELEASE_COMMIT = re.compile(r"chore\(release\): v(\d+\.\d+\.\d+)")
MANIFEST_VERSION = re.compile(r'("version"\s*:\s*)"[^"]*"')
BREAKING, FEATURE, FIX = 3, 2, 1

Plan = namedtuple("Plan", ["version", "deciding", "unconventional"])
Plan.__doc__ = """The release a run should make.

version: the "X.Y.Z" to release.
deciding: the subjects of the commits that raised the version, oldest first.
unconventional: the subjects with no conventional type prefix, oldest first.
"""


def _subject(message):
    return message.strip().split("\n", 1)[0].strip()


def _raise_kind(message):
    """How much a commit raises the version: BREAKING, FEATURE, FIX, 0, or None if unconventional."""
    match = CONVENTIONAL.match(_subject(message))
    if not match:
        return None
    body = message.strip().split("\n")[1:]
    if match.group(3) or any(line.startswith("BREAKING CHANGE:") for line in body):
        return BREAKING
    return {"feat": FEATURE, "fix": FIX}.get(match.group(1).lower(), 0)


def _numbers(version):
    return tuple(int(n) for n in version.split("."))


def _version_text(numbers):
    return ".".join(str(n) for n in numbers)


def _released_messages(messages):
    """The messages a release covers: up to an unfinished release commit, or all of them."""
    for index, message in enumerate(messages):
        if RELEASE_COMMIT.fullmatch(_subject(message)):
            return messages[:index]
    return messages


def last_release(tags):
    """Return the highest release among git tag names, without its "v", or None.

    Only tags shaped "vX.Y.Z" count, and they compare as numbers, so "v1.10.0"
    beats "v1.9.0". Any other tag is skipped. No release tag returns None.
    """
    found = [tuple(int(n) for n in m.groups()) for m in map(TAG.fullmatch, tags) if m]
    if not found:
        return None
    return _version_text(max(found))


def plan_release(last, messages):
    """Decide the next release from the commit messages since the last one.

    last is the last released "X.Y.Z", or None when nothing was ever released.
    messages are full commit messages, subject then body, oldest first.

    A subject is conventional when it starts with a type word, an optional
    "(scope)", an optional "!", then ":". The type matches in any case. A commit
    is breaking when its type carries "!" or its body has a line starting
    "BREAKING CHANGE:". Breaking raises major, "feat" raises minor, "fix" raises
    patch, and every lower number resets to 0. Any other type raises nothing.

    With last as None the version is "1.0.0" whatever the commits say. A
    "chore(release): vX.Y.Z" commit marks a release a failed run left unfinished,
    and the version is then that X.Y.Z, so a re-run finishes it.

    Raises ValueError, with the reason as its message, when last is set and no
    commit raises the version, when more than one release commit is present, or
    when a release commit names a version not above last.
    """
    unconventional = [_subject(m) for m in messages if _raise_kind(m) is None]
    unfinished = [
        match.group(1) for match in (RELEASE_COMMIT.fullmatch(_subject(m)) for m in messages) if match
    ]
    if len(unfinished) > 1:
        raise ValueError(f"more than one release commit since the last tag: {', '.join(unfinished)}")
    covered = _released_messages(messages)
    deciding = [_subject(m) for m in covered if _raise_kind(m)]

    if unfinished:
        version = unfinished[0]
        if last is not None and _numbers(version) <= _numbers(last):
            raise ValueError(f"release commit names v{version}, which is not above v{last}")
        return Plan(version, deciding, unconventional)
    if last is None:
        return Plan("1.0.0", deciding, unconventional)

    kind = max((_raise_kind(m) or 0 for m in covered), default=0)
    if not kind:
        raise ValueError(f"no feat, fix, or breaking change since v{last}, so there is nothing to release")
    major, minor, patch = _numbers(last)
    if kind == BREAKING:
        version = (major + 1, 0, 0)
    elif kind == FEATURE:
        version = (major, minor + 1, 0)
    else:
        version = (major, minor, patch + 1)
    return Plan(_version_text(version), deciding, unconventional)


def release_notes(messages):
    """Return the Markdown body of the GitHub release page for these commits.

    Headings "Breaking changes", "Features" and "Fixes", in that order, each
    listing the subjects without their type prefix, so "feat: Add x (#27)" reads
    "Add x (#27)". A breaking commit is listed under "Breaking changes" only. A
    heading with no entries is left out. Commits that raise nothing are left out.
    """
    groups = {BREAKING: [], FEATURE: [], FIX: []}
    for message in messages:
        kind = _raise_kind(message)
        if kind:
            text = _subject(message)
            groups[kind].append(text[CONVENTIONAL.match(text).end():].strip())
    sections = []
    for kind, heading in ((BREAKING, "Breaking changes"), (FEATURE, "Features"), (FIX, "Fixes")):
        if groups[kind]:
            sections.append(f"## {heading}\n\n" + "\n".join(f"- {entry}" for entry in groups[kind]))
    return "\n\n".join(sections) + "\n"


def write_version(version, root=ROOT):
    """Write version into the three plugin manifests under root.

    The manifests are the max entry in .claude-plugin/marketplace.json, which
    gains a "version" if it has none, plugins/max/plugin.json, and
    ci/.claude-plugin/plugin.json. Nothing else in those files changes, and
    writing the version they already hold changes nothing.

    Raises ValueError when version is not "X.Y.Z" or a manifest is missing.
    """
    if not VERSION.fullmatch(version):
        raise ValueError(f"version must be X.Y.Z, not {version!r}")
    root = Path(root)
    catalog = root / CATALOG
    manifests = [root / m for m in PLUGIN_MANIFESTS]
    missing = [str(p) for p in [catalog] + manifests if not p.is_file()]
    if missing:
        raise ValueError(f"missing manifest: {', '.join(missing)}")
    _write_catalog_version(catalog, version)
    for manifest in manifests:
        _write_manifest_version(manifest, version)


def _write_catalog_version(path, version):
    """Set the max entry's version, placing a new one right after its name."""
    catalog = json.loads(path.read_text())
    entries = [p for p in catalog.get("plugins", []) if p.get("name") == "max"]
    if len(entries) != 1:
        raise ValueError(f"{CATALOG} needs exactly one max plugin")
    entry = entries[0]
    if entry.get("version") == version:
        return
    if "version" in entry:
        entry["version"] = version
    else:
        updated = {}
        for key, value in entry.items():
            updated[key] = value
            if key == "name":
                updated["version"] = version
        entry.clear()
        entry.update(updated)
    path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")


def _write_manifest_version(path, version):
    """Replace the version in a plugin.json as text, so the rest keeps its bytes."""
    text = path.read_text()
    if json.loads(text).get("version") == version:
        return
    if not MANIFEST_VERSION.search(text):
        raise ValueError(f"no version field in {path}")
    path.write_text(MANIFEST_VERSION.sub(lambda m: f'{m.group(1)}"{version}"', text, count=1))


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def _history():
    """The last release and the full commit messages since its tag, oldest first."""
    last = last_release(_git("tag", "--list").split())
    span = [f"v{last}..HEAD"] if last else ["HEAD"]
    log = _git("log", "--reverse", "--format=%B%x00", *span)
    return last, [m.strip() for m in log.split("\0") if m.strip()]


def main():
    """Command line for the release workflow.

    plan                  print the next version, the commits that decided it,
                          and the unconventional commits, read from git since
                          the last vX.Y.Z tag
    plan --version-only   print only the next version
    notes                 print the release notes for the commits since the last tag
    write VERSION         write VERSION into the three plugin manifests

    Any ValueError prints "error: <reason>" and exits 1.
    """
    args = sys.argv[1:]
    if args == ["plan"] or args == ["plan", "--version-only"]:
        last, messages = _history()
        plan = plan_release(last, messages)
        if "--version-only" in args:
            print(plan.version)
            return
        print(f"Last release: {'v' + last if last else 'none'}")
        print(f"Next release: v{plan.version}")
        print("\nCommits that decided it:")
        print("\n".join(f"  {s}" for s in plan.deciding) or "  none")
        print("\nCommits without a conventional type, which raise nothing:")
        print("\n".join(f"  {s}" for s in plan.unconventional) or "  none")
    elif args == ["notes"]:
        _, messages = _history()
        print(release_notes(_released_messages(messages)), end="")
    elif len(args) == 2 and args[0] == "write":
        write_version(args[1])
    else:
        raise ValueError("usage: release.py plan [--version-only] | notes | write VERSION")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
