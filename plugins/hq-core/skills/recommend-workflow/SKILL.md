---
name: recommend-workflow
description: Use when an engineer describes what they're working on and wants to know which skills and workflow to use. Maps a free-text task to the org's skills and workflow playbooks, then offers to install anything missing.
---

# Recommend Workflow

Turn "what I'm working on" into "use these skills, in this order."

## Inputs (all bundled in this plugin)

- `catalog.json` — every first-party skill (name, plugin, tags, description) plus
  referenced external skills (e.g. superpowers). Generated from `taxonomy.yml`.
- `workflows/*.md` — curated playbooks: recommended skill *combinations* per
  task-type, with a Mermaid diagram.

## Steps

1. **Read** `catalog.json` and the list of `workflows/`.
2. **Match the task.** First try to map the engineer's description to a workflow
   playbook (the curated path — prefer these). If none fits, fall back to tag
   matching: infer the task-tags, then list catalog skills carrying those tags.
3. **Recommend.** Show the matched playbook (or skill set) and explain *why* each
   skill is in the path. Name the plugin each skill lives in.
4. **Check what's installed** vs. what the recommendation needs:
   ```shell
   claude plugin list
   ```
5. **Offer to install** anything missing — advise first, install only on accept:
   ```shell
   claude plugin install <plugin>@hq          # optional hq plugins
   claude plugin install superpowers          # referenced dependency
   ```
6. **Hand off.** If a playbook matched, offer to run it as a guided walkthrough.

## Rules

- Recommend from the catalog, not memory — capabilities change as skills are added.
- Don't install without an explicit yes.
- If nothing matches, say so and suggest the closest playbook rather than forcing a fit.
