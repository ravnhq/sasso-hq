---
description: Spawn an autonomous worker on an already-filed issue in the current repo.
argument-hint: <issue-number>
allowed-tools: Bash
---

The user wants to adopt issue **#$ARGUMENTS** from the current repo's `$ISSUES_REPO`.

## 1. Show the issue

```bash
gh issue view $ARGUMENTS
```

Display the title + body. Ask:

> Dispatch a worker on this issue? (yes / no)

## 2. Dispatch

If yes:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.sh" --adopt $ARGUMENTS
```

The script picks the first idle slot, lazily creates the worktree, sets up
`task/$ARGUMENTS` off origin/<default>, and spawns the worker via the configured
dispatcher.

## 3. Report

Slot id, branch name, dispatcher, workspace name. If no idle slots, offer `/pool add <N>`.
