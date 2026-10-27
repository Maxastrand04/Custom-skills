#!/usr/bin/env python3
"""Pick the next release version from conventional commits and write it. No extra packages."""

import sys
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

Plan = namedtuple("Plan", ["version", "deciding", "unconventional"])
Plan.__doc__ = """The release a run should make.

version: the "X.Y.Z" to release.
deciding: the subjects of the commits that raised the version, oldest first.
unconventional: the subjects with no conventional type prefix, oldest first.
"""


def last_release(tags):
    """Return the highest release among git tag names, without its "v", or None.

    Only tags shaped "vX.Y.Z" count, and they compare as numbers, so "v1.10.0"
    beats "v1.9.0". Any other tag is skipped. No release tag returns None.
    """
    raise NotImplementedError


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
    raise NotImplementedError


def release_notes(messages):
    """Return the Markdown body of the GitHub release page for these commits.

    Headings "Breaking changes", "Features" and "Fixes", in that order, each
    listing the subjects without their type prefix, so "feat: Add x (#27)" reads
    "Add x (#27)". A breaking commit is listed under "Breaking changes" only. A
    heading with no entries is left out. Commits that raise nothing are left out.
    """
    raise NotImplementedError


def write_version(version, root=ROOT):
    """Write version into the three plugin manifests under root.

    The manifests are the max entry in .claude-plugin/marketplace.json, which
    gains a "version" if it has none, plugins/max/plugin.json, and
    ci/.claude-plugin/plugin.json. Nothing else in those files changes, and
    writing the version they already hold changes nothing.

    Raises ValueError when version is not "X.Y.Z" or a manifest is missing.
    """
    raise NotImplementedError


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
    raise NotImplementedError


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
