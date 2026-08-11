#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.claude/skills"

mkdir -p "$SKILLS_DIR"

failure=0

extract_frontmatter_field() {
    local file="$1"
    local field="$2"
    awk -v field="$field" '
        BEGIN { in_fm = 0; fm_seen = 0 }
        /^---[[:space:]]*$/ {
            if (fm_seen == 0) { in_fm = 1; fm_seen = 1; next }
            else if (in_fm == 1) { exit }
        }
        in_fm == 1 {
            if (match($0, "^" field ":[[:space:]]*")) {
                value = substr($0, RLENGTH + 1)
                sub(/[[:space:]]+$/, "", value)
                print value
                exit
            }
        }
    ' "$file"
}

install_skill() {
    local skill_dir="$1"
    local name
    name="$(basename "$skill_dir")"
    local skill_md="$skill_dir/SKILL.md"
    local target="$SKILLS_DIR/$name"

    if [[ ! -f "$skill_md" ]]; then
        echo "✗ $name: missing SKILL.md"
        failure=1
        return
    fi

    local fm_name fm_desc
    fm_name="$(extract_frontmatter_field "$skill_md" "name")"
    fm_desc="$(extract_frontmatter_field "$skill_md" "description")"

    if [[ -z "$fm_name" ]]; then
        echo "✗ $name: frontmatter missing 'name'"
        failure=1
        return
    fi
    if [[ -z "$fm_desc" ]]; then
        echo "✗ $name: frontmatter missing 'description'"
        failure=1
        return
    fi
    if [[ "$fm_name" != "$name" ]]; then
        echo "✗ $name: frontmatter name '$fm_name' does not match directory name '$name'"
        failure=1
        return
    fi

    if [[ -L "$target" ]]; then
        local current
        current="$(readlink "$target")"
        if [[ "$current" == "$skill_dir" ]]; then
            echo "✓ $name already installed"
            return
        elif [[ "$current" == "$REPO_DIR"/* ]]; then
            # Points somewhere else inside this repo — the Skill moved between
            # category directories. Re-point rather than fail.
            ln -sfn "$skill_dir" "$target"
            echo "↻ $name re-pointed → $skill_dir"
            return
        else
            echo "⚠ $name: symlink exists but points to '$current' (expected '$skill_dir') — skipping"
            failure=1
            return
        fi
    fi

    if [[ -e "$target" ]]; then
        echo "⚠ $name: a real file or directory exists at '$target' — skipping"
        failure=1
        return
    fi

    ln -s "$skill_dir" "$target"
    echo "✓ $name installed → $target"
}

# Live categories. `archive/` is deliberately absent — archived Skills are kept
# for reference and are never installed.
declare -a CATEGORIES=(kanban developer-tools schoolwork)

# Echo the path of a Skill directory by bare name, searching each category.
resolve_skill() {
    local arg="$1"
    # Allow either a bare name (`implement-tdd`) or a category-qualified path
    # (`developer-tools/implement-tdd`).
    if [[ "$arg" == */* ]]; then
        [[ -d "$REPO_DIR/$arg" ]] && echo "$REPO_DIR/$arg"
        return
    fi
    local category
    for category in "${CATEGORIES[@]}"; do
        if [[ -d "$REPO_DIR/$category/$arg" ]]; then
            echo "$REPO_DIR/$category/$arg"
            return
        fi
    done
}

declare -a skills_to_install=()

if [[ $# -eq 0 ]]; then
    for category in "${CATEGORIES[@]}"; do
        [[ -d "$REPO_DIR/$category" ]] || continue
        for entry in "$REPO_DIR/$category"/*/; do
            entry="${entry%/}"
            if [[ -f "$entry/SKILL.md" ]]; then
                skills_to_install+=("$entry")
            fi
        done
    done
else
    for arg in "$@"; do
        skill_path="$(resolve_skill "$arg")"
        if [[ -z "$skill_path" ]]; then
            echo "✗ $arg: no such Skill in ${CATEGORIES[*]}"
            failure=1
            continue
        fi
        skills_to_install+=("$skill_path")
    done
fi

# Guard the expansion: bash 3.2 (macOS default) treats "${arr[@]}" on an empty
# array as unbound under `set -u`.
if [[ ${#skills_to_install[@]} -gt 0 ]]; then
    for skill_dir in "${skills_to_install[@]}"; do
        install_skill "$skill_dir"
    done
fi

if [[ $failure -ne 0 ]]; then
    exit 1
fi
exit 0
