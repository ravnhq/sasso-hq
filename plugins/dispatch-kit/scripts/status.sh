#!/usr/bin/env bash
# Print worktree pool state + open PRs + open issues for the current repo.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"

require_jq; require_gh; ensure_pool
[ -n "$ISSUES_REPO" ] || { echo "ISSUES_REPO is empty — set it in .claude/brain/config.sh." >&2; exit 1; }

echo "## Slots (dispatcher: $DISPATCHER)"
{
  echo -e "id\tstatus\tissue\tbranch\tworkspace\tpath"
  jq -r '
    .slots[] |
    [ .id, .status, (.issue // "-"), (.branch // "-"), (.workspace // "-"), .path ] | @tsv
  ' "$POOL_FILE"
} | column -t -s $'\t'

echo
echo "## Open PRs ($ISSUES_REPO)"
{
  echo -e "#\tstate\tbranch\tci\ttitle"
  # shellcheck disable=SC2016  # $c/$r are jq variables, not shell expansions
  gh pr list -R "$ISSUES_REPO" --json number,title,headRefName,isDraft,statusCheckRollup \
    --jq '
      .[] | [
        .number,
        (if .isDraft then "draft" else "open" end),
        .headRefName,
        (
          (.statusCheckRollup // []) as $c |
          if ($c | length) == 0 then "-"
          else
            ([$c[] | (.conclusion // .status)]) as $r |
            if ($r | any(. == "FAILURE" or . == "TIMED_OUT" or . == "CANCELLED")) then "fail"
            elif ($r | any(. == "PENDING" or . == "IN_PROGRESS" or . == "QUEUED")) then "running"
            elif ($r | all(. == "SUCCESS" or . == "NEUTRAL" or . == "SKIPPED")) then "green"
            else "mixed" end
          end
        ),
        .title
      ] | @tsv'
} | column -t -s $'\t'

echo
echo "## Open issues ($ISSUES_REPO)"
gh issue list -R "$ISSUES_REPO" --state open --json number,title --jq '.[] | "  #\(.number) — \(.title)"' | head -20
