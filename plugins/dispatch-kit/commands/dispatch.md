---
description: Draft an issue from a one-liner (via the SDD spec skills), get approval, file it in the current repo, and spawn an autonomous worker in a fresh worktree.
argument-hint: <one-liner description of the task>
allowed-tools: Read, Grep, Glob, Bash, Write, Skill
---

The user wants to dispatch this task: **$ARGUMENTS**

You are acting as the **orchestrator** for the current repo. You file an issue and
hand it to an autonomous worker; you do not implement it yourself. Follow this flow
exactly — do not skip the review gate.

## Mental model

Issues + PRs both live in `$ISSUES_REPO` (this repo by default). A worker takes one
issue, gets a git worktree on `task/<N>`, implements it test-first, opens one PR,
comments on the issue, and stops. You (with the human) review and merge.

## 1. Draft the issue body

Reuse the house spec pipeline rather than ad-hoc drafting:

- **Non-trivial** task (3+ steps or an architectural decision): invoke the `to-prd`
  skill to synthesise a PRD, then `to-issues` to slice it into independently-grabbable
  issues. You may then dispatch each resulting issue to a free slot.
- **Trivial** one-liner (typo, single-line tweak): draft the issue inline using
  `${CLAUDE_PLUGIN_ROOT}/templates/issue.md` as the skeleton.

## 2. Show the draft and WAIT for approval

Print the proposed title and body, then ask:

> Ship this issue as-is, or want edits? (reply with edits or "ship it")

Apply edits and re-confirm. **Do not call dispatch.sh until the user explicitly approves.**

## 3. File the issue and dispatch

Once approved, for each issue:

1. Write the final body to a temp file, e.g. `/tmp/issue-body.md`.
2. Run:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.sh" --create-issue \
     --title "<final title>" \
     --body-file /tmp/issue-body.md
   ```
   The script files the issue, picks the first idle slot, lazily creates the
   worktree on `task/<N>` off origin/<default>, renders the worker prompt, and
   spawns a worker via the configured dispatcher (cmux by default).

## 4. Report

Concisely: issue #N + URL, slot id, branch `task/N`, dispatcher, workspace name.

If `dispatch.sh` says no idle slots, offer `/pool add <N>` to expand.
