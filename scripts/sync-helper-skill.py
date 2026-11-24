#!/usr/bin/env python3
"""Copy base skill files into kanban/helper-skill/. No extra packages."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "kanban" / "helper-skill"
ORIGINALS = {
    "ticket-pr.md": ROOT / "kanban" / "pr-ticket" / "ticket-pr.md",
    "RECORD-FORMAT.md": ROOT / "kanban" / "grill-docs" / "RECORD-FORMAT.md",
    "ticket-shapes.md": ROOT / "kanban" / "new-ticket" / "ticket-shapes.md",
}


def stale_copies():
    return [name for name, original in ORIGINALS.items()
            if not (HELPER / name).is_file() or (HELPER / name).read_bytes() != original.read_bytes()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="List stale copies without writing")
    args = parser.parse_args()
    stale = stale_copies()
    if args.check:
        if stale:
            print(f"error: stale copies in kanban/helper-skill: {', '.join(stale)}. "
                  "Run python3 scripts/sync-helper-skill.py", file=sys.stderr)
            sys.exit(1)
        print("Helper skill copies match their originals")
        return
    for name in stale:
        (HELPER / name).write_bytes(ORIGINALS[name].read_bytes())
    print(f"Refreshed {len(stale)} of {len(ORIGINALS)} copies in kanban/helper-skill")


if __name__ == "__main__":
    main()
