#!/bin/sh
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name // "unknown"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
tok_used=$(echo "$input" | jq -r '(.context_window.current_usage | (.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens)) // empty')
five=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
week=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

reset="\033[0m"
dim="\033[2m"

out="$model"

# context-usage bar, capped at 150000 tokens (not the model's max window)
cap=150000
if [ -n "$tok_used" ]; then
  pct=$(( tok_used * 100 / cap ))
  over=0
  if [ "$pct" -ge 100 ]; then
    pct=100
    over=1
  fi
  filled=$(( pct / 10 ))
  [ "$filled" -gt 10 ] && filled=10
  empty=$(( 10 - filled ))
  bar=""
  i=0
  while [ $i -lt $filled ]; do bar="${bar}█"; i=$(( i + 1 )); done
  i=0
  while [ $i -lt $empty ]; do bar="${bar}░"; i=$(( i + 1 )); done
  if [ "$pct" -lt 50 ]; then
    color="\033[2;32m"
  elif [ "$pct" -lt 75 ]; then
    color="\033[2;33m"
  else
    color="\033[2;31m"
  fi
  tok_k=$(awk "BEGIN {printf \"%.1fk\", $tok_used / 1000}")
  if [ "$over" -eq 1 ]; then
    label="FULL (${tok_k}/150k)"
  else
    label="${pct}% (${tok_k}/150k)"
  fi
  ctx_bar="$(printf "${color}[${bar}]${reset}")"
  out="$out | ctx:${ctx_bar} ${label}"
fi

if [ -n "$five" ]; then
  five_pct=$(printf '%.0f' "$five")
  five_filled=$(( five_pct / 10 ))
  [ "$five_filled" -gt 10 ] && five_filled=10
  five_empty=$(( 10 - five_filled ))
  five_bar=""
  i=0
  while [ $i -lt $five_filled ]; do five_bar="${five_bar}█"; i=$(( i + 1 )); done
  i=0
  while [ $i -lt $five_empty ]; do five_bar="${five_bar}░"; i=$(( i + 1 )); done
  if [ "$five_pct" -lt 50 ]; then
    five_color="\033[32m"
  elif [ "$five_pct" -lt 75 ]; then
    five_color="\033[33m"
  else
    five_color="\033[31m"
  fi
  reset="\033[0m"
  five_reset_str=""
  if [ -n "$five_reset" ]; then
    epoch=$(printf '%.0f' "$five_reset" 2>/dev/null)
    if [ -n "$epoch" ] && [ "$epoch" -gt 0 ] 2>/dev/null; then
      now=$(date "+%s")
      diff=$(( epoch - now ))
      if [ "$diff" -gt 0 ]; then
        hrs=$(( diff / 3600 ))
        mins=$(( (diff % 3600) / 60 ))
        remaining=$(printf "%d:%02d" "$hrs" "$mins")
        local_clock=$(date -j -f "%s" "$epoch" "+%H:%M" 2>/dev/null)
        five_reset_str=" (${remaining} left, resets ${local_clock})"
      fi
    fi
  fi
  out="$out | 5h:$(printf "${five_color}[${five_bar}] ${five_pct}%%${reset}")${five_reset_str}"
fi

# cwd (shorten $HOME to ~)
if [ -n "$cwd" ]; then
  disp_cwd=$(printf '%s' "$cwd" | sed "s|^$HOME|~|")
  out="$out | $(printf "${dim}${disp_cwd}${reset}")"
fi

# git branch (skip optional locks, no fetch)
if [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
  if [ -n "$branch" ]; then
    out="$out | $(printf "${dim}(${branch})${reset}")"
  fi
fi

if [ -n "$week" ]; then
  week_pct=$(printf '%.0f' "$week")
  if [ "$week_pct" -lt 50 ]; then
    week_color="\033[32m"
  elif [ "$week_pct" -lt 75 ]; then
    week_color="\033[33m"
  else
    week_color="\033[31m"
  fi
  reset="\033[0m"
  out="$out | weekly: $(printf "${week_color}${week_pct}%%${reset}")"
fi

printf "%b\n" "$out"
