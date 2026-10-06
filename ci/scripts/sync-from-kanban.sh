#!/usr/bin/env bash
# Keeps ci/ in step with kanban/ without ever touching kanban/.
#
#   sync-from-kanban.sh            copy the rule files, print skill drift
#   sync-from-kanban.sh --mark S   record kanban/S/SKILL.md as ported into ci/
#
# Rule files are pure rules, so they are copied byte for byte. Skill files
# differ on purpose, so the script only shows what changed in the kanban
# original since the version ci/ was forked or last synced from. Port the
# parts you want by hand, then --mark the skill.
#
# Each ci SKILL.md records its source as a git blob hash in a comment line:
#   <!-- synced-from kanban/<skill>/SKILL.md blob <hash> -->
# A blob hash names file content, so it survives uncommitted kanban edits.
set -euo pipefail

ROOT="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
cd "$ROOT"

RULE_FILES=(
    "kanban/refactor-ticket/code-standards.md:ci/skills/refactor-ticket/code-standards.md"
    "kanban/architect-ticket/RECORD-FORMAT.md:ci/skills/refactor-ticket/RECORD-FORMAT.md"
    "kanban/unit-test-ticket/test-standards.md:ci/skills/unit-test-ticket/test-standards.md"
    "kanban/pr-ticket/pr-shape.md:ci/skills/pr-ticket/pr-shape.md"
)
SKILLS=(implement-ticket refactor-ticket unit-test-ticket pr-ticket)

marker() { grep -oE 'synced-from kanban/[^ ]+ blob [0-9a-f]{40}' "ci/skills/$1/SKILL.md" | awk '{print $4}'; }

if [[ "${1:-}" == "--mark" ]]; then
    s="${2:?usage: --mark <skill>}"
    src="kanban/$s/SKILL.md" dst="ci/skills/$s/SKILL.md"
    [[ -f "$src" && -f "$dst" ]] || { echo "no $src or $dst" >&2; exit 1; }
    new=$(git hash-object -w "$src")
    old=$(marker "$s")
    sed -i.bak "s/blob $old/blob $new/" "$dst" && rm "$dst.bak"
    echo "$s marked synced at blob ${new:0:10}"
    exit 0
fi

for pair in "${RULE_FILES[@]}"; do
    src="${pair%%:*}" dst="${pair##*:}"
    if ! cmp -s "$src" "$dst"; then
        cp "$src" "$dst"
        echo "copied   $src"
    fi
done

for s in "${SKILLS[@]}"; do
    src="kanban/$s/SKILL.md"
    old=$(marker "$s")
    new=$(git hash-object -w "$src")
    if [[ -z "$old" ]]; then
        echo "no marker  ci/skills/$s/SKILL.md"
    elif [[ "$old" == "$new" ]]; then
        echo "in sync  $s"
    elif ! git cat-file -e "$old" 2>/dev/null; then
        echo "drifted  $s, but blob ${old:0:10} isn't in this clone, so no diff. Compare by hand, then --mark $s."
    else
        echo "drifted  $s. Changes in kanban since the fork:"
        git --no-pager diff "$old" "$new"
        echo
    fi
done
