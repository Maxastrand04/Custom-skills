#!/usr/bin/env bash
# The kanban-ci loop. Runs the station named in HEAD's Handoff-To trailer,
# pushes, runs the whole suite, and repeats until a station hands off to
# review or a halt fires. Then opens the PR. A finished chain gets a body
# written by pr-ticket; a halted one gets a plain body and a draft.
#
# Called by .github/workflows/kanban-ci.yml from inside the project checkout.
#
# Env:
#   BASE              branch the PR targets, default main
#   BRANCH            one ticket branch to run; empty or BASE runs the queue
#   TEST_COMMAND      runs the whole suite, exit 0 means green
#   PLUGIN_DIR        path to the kanban-ci plugin
#   MAX_TURNS_IMPLEMENT, MAX_TURNS_REFACTOR, MAX_TURNS_UNIT_TEST, MAX_TURNS_PR
#   LOG_DIR           where station and suite output goes, default /tmp
set -uo pipefail

BASE="${BASE:-main}"
BRANCH="${BRANCH:-}"
LOG_DIR="${LOG_DIR:-/tmp}"
MAX_BACK_MOVES=2
QUEUE_LABEL="ci:queued"

: "${TEST_COMMAND:?TEST_COMMAND is required}"
: "${PLUGIN_DIR:?PLUGIN_DIR is required}"

log() { printf '[kanban-ci] %s\n' "$*"; }

rank() {
    case "$1" in
        implement-ticket) echo 1 ;;
        refactor-ticket)  echo 2 ;;
        unit-test-ticket) echo 3 ;;
        review)           echo 4 ;;
        *)                echo 0 ;;
    esac
}

model_for() {
    case "$1" in
        refactor-ticket) echo opus ;;
        *)               echo sonnet ;;
    esac
}

max_turns_for() {
    case "$1" in
        implement-ticket) echo "${MAX_TURNS_IMPLEMENT:-150}" ;;
        refactor-ticket)  echo "${MAX_TURNS_REFACTOR:-200}" ;;
        unit-test-ticket) echo "${MAX_TURNS_UNIT_TEST:-150}" ;;
        pr-ticket)        echo "${MAX_TURNS_PR:-40}" ;;
    esac
}

# Last value of a trailer on HEAD, or empty.
trailer() {
    git log -1 --format="%(trailers:key=$1,valueonly)" HEAD | sed '/^[[:space:]]*$/d' | tail -n1 | tr -d '[:space:]'
}

# Runs the whole suite. Sets SUITE_GREEN (0/1) and SUITE_SUMMARY.
run_suite() {
    local out="$LOG_DIR/suite.log" rc
    log "running the suite: $TEST_COMMAND"
    bash -c "$TEST_COMMAND" >"$out" 2>&1
    rc=$?
    if [[ $rc -eq 0 ]]; then
        SUITE_GREEN=1
        SUITE_SUMMARY="Suite summary: all pass."
    else
        SUITE_GREEN=0
        SUITE_SUMMARY="Suite summary: failed, exit $rc. Last 80 lines of output:
$(tail -n 80 "$out")"
    fi
    # A test run may touch tracked files, such as snapshots. Station work is
    # already committed, so drop whatever the run left.
    git reset --hard -q HEAD
}

# Runs one station. Returns 0 on a normal exit, 2 on a usage limit, 1 otherwise.
run_station() {
    local station="$1" note="$2" out rc
    out="$LOG_DIR/$station.json"
    local prompt="/kanban-ci:$station #$ISSUE base:$BASE"
    [[ -n "$note" ]] && prompt="$prompt

$note"
    log "starting $station on $(model_for "$station")"
    claude -p "$prompt" \
        --plugin-dir "$PLUGIN_DIR" \
        --model "$(model_for "$station")" \
        --max-turns "$(max_turns_for "$station")" \
        --permission-mode bypassPermissions \
        --output-format json >"$out" 2>&1
    rc=$?
    # Unverified against a real limit hit: matches the wording Claude Code
    # has used for subscription limits. Tune once a real one shows up in a log.
    if grep -qiE 'usage limit|limit reached|out of usage|5-hour limit|weekly limit' "$out"; then
        return 2
    fi
    [[ $rc -eq 0 ]] && return 0 || return 1
}

# Every station's "For the reviewer" section, oldest first.
reviewer_items() {
    local sha subject items
    for sha in $(git rev-list --reverse "origin/$BASE..HEAD"); do
        items=$(git log -1 --format=%B "$sha" | awk '/^For the reviewer[[:space:]]*$/ {f=1; next} f && /^[[:space:]]*$/ {f=0} f {print}')
        [[ -z "$items" ]] && continue
        subject=$(git log -1 --format=%s "$sha")
        printf '**%s** `%s`\n\n%s\n\n' "$subject" "$(git rev-parse --short "$sha")" "$items"
    done
}

# Has pr-ticket write the Summary, Evidence and Merge danger sections to
# $LOG_DIR/pr-summary.md. Leaves no file when the suite is red or the station
# fails, and open_pr falls back to the plain body.
write_summary() {
    local out="$LOG_DIR/pr-summary.md" before
    rm -f "$out"
    # A chain resumed straight at review never ran the suite this run.
    [[ -z "${SUITE_SUMMARY:-}" ]] && run_suite
    [[ $SUITE_GREEN -eq 1 ]] || return 0
    before=$(git rev-parse HEAD)
    run_station pr-ticket "Write the body to $out.

$SUITE_SUMMARY" || log "pr-ticket failed, using the plain body"
    # pr-ticket never commits. Drop anything it left so the PR is the chain's work.
    git reset --hard -q "$before"
}

# Opens or updates the PR. $1 is empty when finished, else the halt reason.
open_pr() {
    local halt="$1" body="$LOG_DIR/pr-body.md" summary="$LOG_DIR/pr-summary.md" title pr status items
    rm -f "$summary"
    [[ -z "$halt" ]] && write_summary
    title=$(gh issue view "$ISSUE" --json title --jq .title)
    if [[ -z "$halt" ]]; then status="Finished."; else status="Halted: $halt"; fi
    items=$(reviewer_items)
    {
        printf '> *Implemented by the kanban-ci loop with nobody watching. Run `/kanban-ci:review-ticket` on this PR before merging.*\n\n'
        printf 'Closes #%s\n\n' "$ISSUE"
        printf '**Status** %s\n\n' "$status"
        printf '**Route** %s\n\n' "${ROUTE[*]:-none}"
        if [[ -s "$summary" ]]; then cat "$summary"; printf '\n'; fi
        printf '## For the reviewer\n\n'
        if [[ -n "$items" ]]; then printf '%s\n' "$items"; else printf 'none\n\n'; fi
        if [[ -n "$halt" ]]; then
            printf '## Last handoff\n\n```\n%s\n```\n' "$(git log -1 --format=%B HEAD)"
        fi
    } >"$body"

    pr=$(gh pr list --head "$TICKET_BRANCH" --state open --json number --jq '.[0].number // empty')
    if [[ -n "$pr" ]]; then
        gh pr edit "$pr" --body-file "$body" >/dev/null
        if [[ -n "$halt" ]]; then gh pr ready "$pr" --undo >/dev/null 2>&1; else gh pr ready "$pr" >/dev/null 2>&1; fi
    else
        local draft=""
        [[ -n "$halt" ]] && draft="--draft"
        gh pr create --base "$BASE" --head "$TICKET_BRANCH" --title "$title" --body-file "$body" $draft >/dev/null
        pr=$(gh pr list --head "$TICKET_BRANCH" --state open --json number --jq '.[0].number // empty')
    fi
    gh issue edit "$ISSUE" --remove-label "$QUEUE_LABEL" >/dev/null 2>&1 || true
    log "PR #$pr, $status"
}

# Runs one ticket branch to the end. Returns 2 when the usage limit stopped it.
run_ticket() {
    TICKET_BRANCH="$1"
    ISSUE="${TICKET_BRANCH%%-*}"
    ROUTE=()
    SUITE_SUMMARY="" SUITE_GREEN=0
    log "ticket #$ISSUE on $TICKET_BRANCH"

    git fetch -q origin "$TICKET_BRANCH" "$BASE" || { log "can't fetch $TICKET_BRANCH"; return 1; }
    git checkout -q -B "$TICKET_BRANCH" "origin/$TICKET_BRANCH"

    local next back=0 retried="" note="" before to from rc
    next=$(trailer Handoff-To)
    if [[ -z "$next" ]]; then
        log "HEAD has no Handoff-To trailer. Run /kanban-ci:launch on the branch first. Skipping."
        return 1
    fi

    # Resuming mid-chain, as after a usage limit: the station still needs
    # the suite result it would normally get from the run before it.
    if [[ "$next" != implement-ticket && "$next" != review ]]; then
        run_suite
        note="$SUITE_SUMMARY"
    fi

    while [[ "$next" != review ]]; do
        if [[ $(rank "$next") -eq 0 ]]; then
            open_pr "unknown station in Handoff-To: $next"
            return 0
        fi
        ROUTE+=("$next")
        before=$(git rev-parse HEAD)

        run_station "$next" "$note"
        rc=$?
        if [[ $rc -eq 2 ]]; then
            log "usage limit hit in $next. Leaving #$ISSUE queued; the next run resumes from the newest commit."
            git reset --hard -q HEAD
            git push -q origin "$TICKET_BRANCH"
            return 2
        fi

        if [[ "$(git rev-parse HEAD)" == "$before" ]]; then
            git push -q origin "$TICKET_BRANCH"
            open_pr "$next made no handoff commit. It crashed, hit its turn limit, or timed out. See the workflow log."
            return 0
        fi
        if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
            git push -q origin "$TICKET_BRANCH"
            open_pr "$next left uncommitted changes to tracked files after its handoff. See the workflow log."
            return 0
        fi
        git push -q origin "$TICKET_BRANCH"

        to=$(trailer Handoff-To)
        from=$(trailer Handoff-From)
        if [[ -z "$to" ]]; then
            open_pr "$next's last commit has no Handoff-To trailer."
            return 0
        fi
        [[ "$from" != "$next" ]] && log "warning: Handoff-From is '$from', expected '$next'"

        run_suite

        # A handoff that claims done must leave the suite green: refactor to
        # unit-test, and unit-test to review. implement may hand forward red,
        # since stale tests are refactor's to reconcile, and an early handoff
        # to review is a halt that may be red.
        local claims_done=0
        [[ "$next" == refactor-ticket && "$to" == unit-test-ticket ]] && claims_done=1
        [[ "$next" == unit-test-ticket && "$to" == review ]] && claims_done=1
        if [[ $SUITE_GREEN -eq 0 && $claims_done -eq 1 ]]; then
            if [[ "$retried" == "$next" ]]; then
                open_pr "$next handed off as done twice, and the suite was red both times."
                return 0
            fi
            retried="$next"
            note="The loop ran the whole suite after your handoff to $to and it failed. You handed off as done, so the failures came from your session. Fix them, then hand off again.

$SUITE_SUMMARY"
            continue
        fi

        if [[ "$to" != review && $(rank "$to") -lt $(rank "$next") ]]; then
            back=$((back + 1))
            if [[ $back -gt $MAX_BACK_MOVES ]]; then
                open_pr "more than $MAX_BACK_MOVES backward moves. Last: $next sent the work back to $to."
                return 0
            fi
        fi

        retried=""
        note="$SUITE_SUMMARY"
        next="$to"
    done

    if [[ $(trailer Handoff-From) == unit-test-ticket ]]; then
        open_pr ""
    else
        open_pr "$(trailer Handoff-From) handed off to review early. See its commit."
    fi
    return 0
}

# ---------------------------------------------------------------- queue

declare -a TICKETS=()
if [[ -n "$BRANCH" && "$BRANCH" != "$BASE" ]]; then
    TICKETS=("$BRANCH")
else
    for n in $(gh issue list --label "$QUEUE_LABEL" --state open --limit 100 --json number --jq '.[].number' | sort -n); do
        b=$(git ls-remote --heads origin "refs/heads/$n-*" | head -n1 | sed 's#.*refs/heads/##')
        if [[ -z "$b" ]]; then
            log "#$n is queued but has no branch named $n-*. Skipping."
            continue
        fi
        TICKETS+=("$b")
    done
fi

if [[ ${#TICKETS[@]} -eq 0 ]]; then
    log "nothing queued"
    exit 0
fi

for t in "${TICKETS[@]}"; do
    run_ticket "$t"
    if [[ $? -eq 2 ]]; then
        log "stopping the queue for tonight"
        break
    fi
done
exit 0
