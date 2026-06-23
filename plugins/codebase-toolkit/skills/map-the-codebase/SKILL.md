---
name: map-the-codebase
description: Build or refresh an offline structural map of a repo (a code graph) that other skills can read. Use before improve-codebase-architecture, or when you want a real call/import/reference graph of the codebase instead of reasoning from memory.
---

# Map the Codebase

Produce a real structural map of the repo — a code graph of who calls, imports,
references, and contains whom — and leave it in `graphify-out/` for other skills
(notably [improve-codebase-architecture](../improve-codebase-architecture/SKILL.md))
to read. Single responsibility: **produce or refresh the map.** It does not
analyse architecture itself.

The map is built by [graphify](https://github.com/safishamsi/graphify) (MIT),
driven as an **offline, code-only** CLI: tree-sitter AST extraction + local
community detection. No API key, no network, no cost. The graph is a local cache,
not a committed artifact.

## What you get in `graphify-out/`

- `graph.json` — the graph itself (networkx node-link format: `nodes[]` + `links[]`).
- `GRAPH_REPORT.md` — human-readable orientation: God Nodes (most-connected core
  abstractions), communities, import cycles, surprising connections.

## Step 1 — Detect and offer to install (CLI only)

Check whether the CLI is present:

```bash
graphify --version
```

If it is missing, offer to install it and wait for the user before proceeding:

```bash
uv tool install graphifyy   # note the double-y; the PyPI package is `graphifyy`
```

Pin to the `0.8.x` minor line you validated against — graphify is pre-1.0, so a
minor bump can change `graph.json`'s shape. If `--version` reports a different
minor, re-check the recipes in
[improve-codebase-architecture/GRAPH-EVIDENCE.md](../improve-codebase-architecture/GRAPH-EVIDENCE.md)
before trusting them.

**Never run `graphify install`.** That copies graphify's own `/graphify` skill
into the Claude config dir — a competing skill we don't want. We only ever drive
the `graphify` *binary*. (Don't re-add it: this is deliberate.)

## Step 2 — Build the graph, offline and code-only

Run from the repo root. Two commands: `extract` builds and clusters the graph;
`cluster-only` writes `GRAPH_REPORT.md` with placeholder community names (the only
step that would otherwise call an LLM is community *naming*, which `--no-label`
skips).

```bash
graphify extract . \
  --exclude '*.md' --exclude '*.mdx' --exclude '*.qmd' --exclude '*.txt' \
  --exclude '*.rst' --exclude '*.html' --exclude '*.yaml' --exclude '*.yml' \
  --exclude '*.pdf' --exclude '*.png' --exclude '*.jpg' --exclude '*.jpeg' \
  --exclude '*.gif' --exclude '*.webp' --exclude '*.svg' \
  --exclude '*.mp4' --exclude '*.mov' --exclude '*.webm' --exclude '*.mkv' \
  --exclude '*.avi' --exclude '*.m4v' --exclude '*.mp3' --exclude '*.wav' \
  --exclude '*.m4a' --exclude '*.ogg'
graphify cluster-only . --no-label --no-viz
```

Why the long exclude list: graphify treats doc/paper/image files (`.md`, `.yml`,
`.pdf`, `.png`, …) as needing *semantic* (LLM) extraction, and a single one of
them makes the build demand an API key and abort. Excluding them keeps the build
to pure-local code AST. **The patterns must be single-quoted** — unquoted, the
shell expands `*.md` against the cwd and the exclusion silently breaks.

Notes:
- `--no-viz` skips the `graph.html` visualisation (not needed, and large).
- Keep the exclude set identical across runs. graphify's incremental cache lives
  inside `graphify-out/`; changing the excludes between runs confuses it. For a
  clean rebuild, `rm -rf graphify-out` first.
- A code-only repo (no doc/image files) needs no excludes, but passing them is
  harmless and keeps the command uniform.

## Step 3 — Keep the graph out of git

The graph is an ephemeral local cache. Ensure `graphify-out/` is gitignored
(append it to the repo's root `.gitignore` if it's not already there). Do **not**
commit it.

## Step 4 — Report

Tell the user the map is built and where it is: the absolute path to
`graphify-out/GRAPH_REPORT.md` for orientation, and that `graph.json` is now
available for `improve-codebase-architecture` to ground its analysis. Surface one
or two headline signals from the report (e.g. the top God Nodes) so they know it
worked.

## Staleness

The graph is a snapshot. Before relying on an existing one, check it's fresh:

```bash
# stale if any tracked source is newer than the graph, or the tree is dirty
[ graphify-out/graph.json -ot "$(git ls-files | xargs ls -t 2>/dev/null | head -1)" ] && echo "STALE: source newer than graph"
git status --porcelain | grep -q . && echo "STALE: working tree dirty"
```

If stale, say so and offer to rebuild (re-run Step 2). Default to proceeding with
a caveat rather than forcing a rebuild — the user may not care about the latest
edits for a structural overview.
