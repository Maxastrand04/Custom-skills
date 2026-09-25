#!/usr/bin/env python3
# PreInvocation hook. Antigravity has no SessionStart event, so this injects the
# full unslop skill only on the first model call of an execution. The docs do not
# say whether invocationNum resets per user turn or per conversation, so on a
# long conversation this may fire more than once. Harmless, just more tokens.
import json
import os
import sys

try:
    payload = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    payload = {}

if payload.get("invocationNum", 1) != 1:
    print(json.dumps({"injectSteps": []}))
    sys.exit(0)

path = os.path.expanduser("~/.gemini/config/skills/unslop/SKILL.md")
steps = []
if os.path.exists(path):
    with open(path) as f:
        steps.append({"ephemeralMessage": f.read()})

print(json.dumps({"injectSteps": steps}))
