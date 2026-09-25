#!/usr/bin/env python3
import os

path = os.path.expanduser("~/.claude/skills/unslop/SKILL.md")
if os.path.exists(path):
    with open(path) as f:
        print(f.read())
