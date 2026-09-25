#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"
AGY_SKILLS_DIR="${HOME}/.gemini/config/skills"

# Every "is this link ours" check is a string compare against REPO_DIR. macOS
# ignores case on disk, so `cd ~/github/custom-skills` would otherwise make the
# script disown every link it created from ~/GitHub/Custom-skills.
[[ "$(uname)" == "Darwin" ]] && shopt -s nocasematch

# Live categories. `archive/` is deliberately absent — archived Skills are kept
# for reference and are never installed.
declare -a CATEGORIES=(kanban developer-tools behaviour schoolwork)

failure=0

show_help() {
    cat <<EOF
Usage: ./install.sh [--claude] [--agy] [SKILL ...]

Symlink skills from this repo into Claude Code and/or Antigravity (agy).

Targets:
  --claude        Claude Code      (~/.claude/skills)
  --agy           Antigravity      (~/.gemini/config/skills)
  -h, --help      Show this help

With no target flag, both are used.

Interactive (no SKILL arguments, running in a terminal):
  Opens a menu. Pick the agent, then toggle skills. Installed skills are
  pre-selected. The result is a sync: unticked skills are unlinked, and stale
  links (archived or renamed skills) are removed. Only symlinks that point into
  this repo are ever touched. Uses fzf when installed, a numbered list otherwise.

Non-interactive (SKILL arguments given, or no terminal):
  Add-only. Links the named skills, or every live skill when none are named.
  Never removes anything. Stale links are reported, not removed.

Skills are bare names ('grilling') or category-qualified ('behaviour/grilling').

Examples:
  ./install.sh                             # menu (or install-all without a tty)
  ./install.sh --agy                       # menu for Antigravity only
  ./install.sh grilling unslop             # add two skills to both agents
  ./install.sh --claude kanban/map-epic    # add one skill to Claude Code
EOF
}

# ---------------------------------------------------------------- arguments

target_claude=0
target_agy=0
declare -a POSITIONAL_ARGS=()

for arg in "$@"; do
    case "$arg" in
        --claude) target_claude=1 ;;
        --agy)    target_agy=1 ;;
        -h|--help) show_help; exit 0 ;;
        --*) echo "✗ unknown flag: $arg" >&2; show_help >&2; exit 1 ;;
        *) POSITIONAL_ARGS+=("$arg") ;;
    esac
done

interactive=0
if [[ ${#POSITIONAL_ARGS[@]} -eq 0 && -t 0 && -t 1 ]]; then
    interactive=1
fi

# ---------------------------------------------------------------- skill lookup

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

# Echo the path of a Skill directory by bare name, searching each category.
resolve_skill() {
    local arg="$1"
    if [[ "$arg" == */* ]]; then
        [[ -d "$REPO_DIR/$arg" ]] && echo "$REPO_DIR/$arg"
        return 0
    fi
    local category
    for category in "${CATEGORIES[@]}"; do
        if [[ -d "$REPO_DIR/$category/$arg" ]]; then
            echo "$REPO_DIR/$category/$arg"
            return 0
        fi
    done
    return 0
}

validate_skill() {
    local skill_dir="$1"
    local name
    name="$(basename "$skill_dir")"
    local skill_md="$skill_dir/SKILL.md"

    if [[ ! -f "$skill_md" ]]; then
        echo "✗ $name: missing SKILL.md"
        failure=1
        return 1
    fi

    local fm_name fm_desc
    fm_name="$(extract_frontmatter_field "$skill_md" name)"
    fm_desc="$(extract_frontmatter_field "$skill_md" description)"

    if [[ -z "$fm_name" ]]; then
        echo "✗ $name: frontmatter missing 'name'"
        failure=1
        return 1
    fi
    if [[ -z "$fm_desc" ]]; then
        echo "✗ $name: frontmatter missing 'description'"
        failure=1
        return 1
    fi
    if [[ "$fm_name" != "$name" ]]; then
        echo "✗ $name: frontmatter name '$fm_name' does not match directory name '$name'"
        failure=1
        return 1
    fi
    return 0
}

# Every live, valid skill as `category/name`. Invalid ones are reported once
# here and never offered in the menu.
declare -a LIVE_SKILLS=()
collect_live_skills() {
    local category entry
    for category in "${CATEGORIES[@]}"; do
        [[ -d "$REPO_DIR/$category" ]] || continue
        for entry in "$REPO_DIR/$category"/*/; do
            entry="${entry%/}"
            [[ -d "$entry" ]] || continue
            if validate_skill "$entry"; then
                LIVE_SKILLS+=("$category/$(basename "$entry")")
            fi
        done
    done
}

is_live_skill_name() {
    local name="$1" s
    for s in "${LIVE_SKILLS[@]}"; do
        [[ "${s#*/}" == "$name" ]] && return 0
    done
    return 1
}

in_list() {
    local needle="$1"; shift
    local x
    for x in "$@"; do
        [[ "$x" == "$needle" ]] && return 0
    done
    return 1
}

# ---------------------------------------------------------------- linking

link_skill() {
    local rel="$1" target_dir="$2" label="$3"
    local skill_dir="$REPO_DIR/$rel"
    local name="${rel#*/}"
    local target="$target_dir/$name"

    mkdir -p "$target_dir"

    if [[ -L "$target" ]]; then
        local current
        current="$(readlink "$target")"
        if [[ "$current" == "$skill_dir" ]]; then
            echo "✓ $name already installed ($label)"
            return
        elif [[ "$current" == "$REPO_DIR"/* ]]; then
            # Points somewhere else inside this repo — the Skill moved between
            # category directories. Re-point rather than fail.
            ln -sfn "$skill_dir" "$target"
            echo "↻ $name re-pointed ($label) → $skill_dir"
            return
        else
            echo "⚠ $name ($label): symlink exists but points to '$current' — skipping"
            failure=1
            return
        fi
    fi

    if [[ -e "$target" ]]; then
        echo "⚠ $name ($label): a real file or directory exists at '$target' — skipping"
        failure=1
        return
    fi

    ln -s "$skill_dir" "$target"
    echo "✓ $name installed ($label) → $target"
}

# Remove a link only if it is a symlink into this repo. Anything else is
# someone else's and is left alone.
unlink_skill() {
    local name="$1" target_dir="$2" label="$3" why="${4:-unticked}"
    local target="$target_dir/$name"
    if [[ -L "$target" && "$(readlink "$target")" == "$REPO_DIR"/* ]]; then
        rm "$target"
        echo "− $name removed ($label, $why)"
    else
        echo "⚠ $name ($label): not a symlink into this repo — left alone"
    fi
}

# Names currently linked into this repo from a target dir, as `name`.
installed_names() {
    local target_dir="$1" link
    [[ -d "$target_dir" ]] || return 0
    for link in "$target_dir"/*; do
        [[ -L "$link" ]] || continue
        [[ "$(readlink "$link")" == "$REPO_DIR"/* ]] && basename "$link"
    done
}

# Stale = links into this repo whose name is no longer a live skill. Emits
# `name<TAB>reason`.
stale_links() {
    local target_dir="$1" link name dest
    [[ -d "$target_dir" ]] || return 0
    for link in "$target_dir"/*; do
        [[ -L "$link" ]] || continue
        dest="$(readlink "$link")"
        [[ "$dest" == "$REPO_DIR"/* ]] || continue
        name="$(basename "$link")"
        is_live_skill_name "$name" && continue
        if [[ -d "$REPO_DIR/archive/$name" ]]; then
            printf '%s\tarchived\n' "$name"
        elif [[ ! -e "$dest" ]]; then
            printf '%s\tmissing, renamed?\n' "$name"
        else
            printf '%s\tnot a live skill\n' "$name"
        fi
    done
}

# ---------------------------------------------------------------- menus

# Both menus take the live skill list plus the installed set and leave the
# final selection (as `category/name`) in SELECTED. Semantics are the same in
# both: installed skills start ticked, you toggle, enter with nothing toggled
# changes nothing.
declare -a SELECTED=()

pick_agent() {
    echo
    echo "Which agent?"
    echo "  1) Claude Code    ($CLAUDE_SKILLS_DIR)"
    echo "  2) Antigravity    ($AGY_SKILLS_DIR)"
    echo "  3) Both"
    local choice
    while true; do
        read -r -p "> " choice
        case "$choice" in
            1) target_claude=1; return ;;
            2) target_agy=1; return ;;
            3|"") target_claude=1; target_agy=1; return ;;
            *) echo "  1, 2 or 3" ;;
        esac
    done
}

# Needs fzf 0.45 or newer for the `transform` action.
fzf_usable() {
    command -v fzf >/dev/null 2>&1 || return 1
    local v
    v="$(fzf --version | awk '{print $1}')"
    [[ "${v%%.*}" -gt 0 ]] && return 0
    [[ "$(echo "$v" | cut -d. -f2)" -ge 45 ]]
}

# The list lives in a temp file so tab can flip the [x] in place and reload.
# fzf's own multi-select marker is off; the tick inside the line is the state.
pick_skills_fzf() {
    local label="$1"; shift
    local -a installed=("$@")
    local rel name state status
    state="$(mktemp)"

    for rel in "${LIVE_SKILLS[@]}"; do
        name="${rel#*/}"
        if in_list "$name" "${installed[@]+"${installed[@]}"}"; then
            printf '[x] %s\n' "$rel"
        else
            printf '[ ] %s\n' "$rel"
        fi
    done > "$state"

    local flip all none
    flip="awk -v l={} '\$0==l { print (substr(\$0,2,1)==\"x\" ? \"[ ]\" : \"[x]\") substr(\$0,4); next } { print }' \"$state\" > \"$state.tmp\" && mv \"$state.tmp\" \"$state\""
    all="awk '{ print \"[x]\" substr(\$0,4) }' \"$state\" > \"$state.tmp\" && mv \"$state.tmp\" \"$state\""
    none="awk '{ print \"[ ]\" substr(\$0,4) }' \"$state\" > \"$state.tmp\" && mv \"$state.tmp\" \"$state\""

    set +e
    fzf --no-sort --no-multi --layout=reverse --cycle \
        --header "$label: tab toggles, ctrl-a all, ctrl-d none, enter applies, esc cancels" \
        --bind "tab:execute-silent($flip)+reload(cat \"$state\")+transform(echo pos \$(( {n} + 1 )))" \
        --bind "ctrl-a:execute-silent($all)+reload(cat \"$state\")+transform(echo pos \$(( {n} + 1 )))" \
        --bind "ctrl-d:execute-silent($none)+reload(cat \"$state\")+transform(echo pos \$(( {n} + 1 )))" \
        --bind "enter:accept" \
        < "$state" > /dev/null
    status=$?
    set -e

    SELECTED=()
    if [[ $status -eq 130 ]]; then
        # Cancelled. Keep what is installed.
        for rel in "${LIVE_SKILLS[@]}"; do
            in_list "${rel#*/}" "${installed[@]+"${installed[@]}"}" && SELECTED+=("$rel")
        done
    else
        while IFS= read -r line; do
            [[ "$line" == "[x] "* ]] && SELECTED+=("${line#\[x\] }")
        done < "$state"
    fi
    rm -f "$state" "$state.tmp"
}

pick_skills_plain() {
    local label="$1"; shift
    local -a installed=("$@")
    local -a state=()
    local i rel name category last_category input tok

    for rel in "${LIVE_SKILLS[@]}"; do
        name="${rel#*/}"
        if in_list "$name" "${installed[@]+"${installed[@]}"}"; then
            state+=(1)
        else
            state+=(0)
        fi
    done

    while true; do
        echo
        echo "$label"
        last_category=""
        for i in "${!LIVE_SKILLS[@]}"; do
            rel="${LIVE_SKILLS[$i]}"
            category="${rel%%/*}"
            if [[ "$category" != "$last_category" ]]; then
                echo "  $category/"
                last_category="$category"
            fi
            if [[ ${state[$i]} -eq 1 ]]; then
                printf '    %2d) [x] %s\n' "$((i + 1))" "${rel#*/}"
            else
                printf '    %2d) [ ] %s\n' "$((i + 1))" "${rel#*/}"
            fi
        done
        echo
        echo "  Numbers or a category name toggle. 'all' / 'none'. Enter applies."
        read -r -p "> " input
        [[ -z "$input" ]] && break
        for tok in $input; do
            case "$tok" in
                all)  for i in "${!state[@]}"; do state[$i]=1; done ;;
                none) for i in "${!state[@]}"; do state[$i]=0; done ;;
                *[!0-9]*)
                    if in_list "$tok" "${CATEGORIES[@]}"; then
                        for i in "${!LIVE_SKILLS[@]}"; do
                            [[ "${LIVE_SKILLS[$i]%%/*}" == "$tok" ]] && state[$i]=$((1 - state[$i]))
                        done
                    else
                        echo "  ? $tok"
                    fi
                    ;;
                *)
                    if [[ $tok -ge 1 && $tok -le ${#LIVE_SKILLS[@]} ]]; then
                        i=$((tok - 1)); state[$i]=$((1 - state[$i]))
                    else
                        echo "  ? $tok"
                    fi
                    ;;
            esac
        done
    done

    SELECTED=()
    for i in "${!LIVE_SKILLS[@]}"; do
        [[ ${state[$i]} -eq 1 ]] && SELECTED+=("${LIVE_SKILLS[$i]}")
    done
}

# Menu, plan, confirm, apply. One target at a time so a removal is always one
# you looked at.
sync_target() {
    local target_dir="$1" label="$2"
    local -a installed=() to_add=() to_remove=() stale=()
    local name rel line

    while IFS= read -r name; do
        [[ -n "$name" ]] && installed+=("$name")
    done < <(installed_names "$target_dir")

    while IFS= read -r line; do
        [[ -n "$line" ]] && stale+=("$line")
    done < <(stale_links "$target_dir")

    if fzf_usable; then
        pick_skills_fzf "$label" "${installed[@]+"${installed[@]}"}"
    else
        pick_skills_plain "$label" "${installed[@]+"${installed[@]}"}"
    fi

    for rel in "${SELECTED[@]+"${SELECTED[@]}"}"; do
        in_list "${rel#*/}" "${installed[@]+"${installed[@]}"}" || to_add+=("$rel")
    done
    for name in "${installed[@]+"${installed[@]}"}"; do
        is_live_skill_name "$name" || continue   # stale, handled below
        local keep=0
        for rel in "${SELECTED[@]+"${SELECTED[@]}"}"; do
            [[ "${rel#*/}" == "$name" ]] && keep=1
        done
        [[ $keep -eq 0 ]] && to_remove+=("$name")
    done

    echo
    echo "Plan for $label ($target_dir):"
    if [[ ${#to_add[@]} -eq 0 && ${#to_remove[@]} -eq 0 && ${#stale[@]} -eq 0 ]]; then
        echo "  nothing to change"
        return
    fi
    for rel in "${to_add[@]+"${to_add[@]}"}";        do echo "  + ${rel#*/}"; done
    for name in "${to_remove[@]+"${to_remove[@]}"}"; do echo "  − $name"; done
    for line in "${stale[@]+"${stale[@]}"}";         do echo "  − ${line%%	*}  (stale: ${line#*	})"; done

    local yn
    read -r -p "Apply? [y/N] " yn
    [[ "$yn" == [yY]* ]] || { echo "  skipped"; return; }

    for rel in "${to_add[@]+"${to_add[@]}"}";        do link_skill "$rel" "$target_dir" "$label"; done
    for name in "${to_remove[@]+"${to_remove[@]}"}"; do unlink_skill "$name" "$target_dir" "$label"; done
    for line in "${stale[@]+"${stale[@]}"}";         do unlink_skill "${line%%	*}" "$target_dir" "$label" "${line#*	}"; done
}

# Add-only. Used for explicit skill arguments and for the no-tty case.
add_to_target() {
    local target_dir="$1" label="$2"; shift 2
    local rel line
    for rel in "$@"; do
        link_skill "$rel" "$target_dir" "$label"
    done
    while IFS= read -r line; do
        [[ -n "$line" ]] || continue
        echo "⚠ ${line%%	*} ($label): stale link, ${line#*	}. Run ./install.sh in a terminal to clean up."
    done < <(stale_links "$target_dir")
}

# ---------------------------------------------------------------- main

collect_live_skills

if [[ $interactive -eq 1 ]]; then
    if [[ $target_claude -eq 0 && $target_agy -eq 0 ]]; then
        pick_agent
    fi
    [[ $target_claude -eq 1 ]] && sync_target "$CLAUDE_SKILLS_DIR" "claude"
    [[ $target_agy -eq 1 ]]    && sync_target "$AGY_SKILLS_DIR" "agy"
else
    if [[ $target_claude -eq 0 && $target_agy -eq 0 ]]; then
        target_claude=1; target_agy=1
    fi

    declare -a to_install=()
    if [[ ${#POSITIONAL_ARGS[@]} -eq 0 ]]; then
        to_install=("${LIVE_SKILLS[@]+"${LIVE_SKILLS[@]}"}")
    else
        for arg in "${POSITIONAL_ARGS[@]}"; do
            skill_path="$(resolve_skill "$arg")"
            if [[ -z "$skill_path" ]]; then
                echo "✗ $arg: no such Skill in ${CATEGORIES[*]}"
                failure=1
                continue
            fi
            rel="${skill_path#"$REPO_DIR"/}"
            if in_list "$rel" "${LIVE_SKILLS[@]+"${LIVE_SKILLS[@]}"}"; then
                to_install+=("$rel")
            else
                # Resolved to a directory, but it failed validation above or
                # sits outside the live categories.
                echo "✗ $arg: not a valid live skill"
                failure=1
            fi
        done
    fi

    if [[ ${#to_install[@]} -gt 0 ]]; then
        [[ $target_claude -eq 1 ]] && add_to_target "$CLAUDE_SKILLS_DIR" "claude" "${to_install[@]}"
        [[ $target_agy -eq 1 ]]    && add_to_target "$AGY_SKILLS_DIR" "agy" "${to_install[@]}"
    fi
fi

if [[ $failure -ne 0 ]]; then
    exit 1
fi
exit 0
