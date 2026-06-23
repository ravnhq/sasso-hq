# Graph evidence

Optional structural signals from a [map-the-codebase](../map-the-codebase/SKILL.md)
graph (`graphify-out/graph.json`). These **inform** the Explore step — they point
you at modules worth applying the deletion test to. They are inputs to judgment,
never verdicts. A high number here is a *question*, not a finding. Confirm
everything by reading the code.

If `graphify-out/graph.json` is absent, skip all of this and explore organically.

## Reading the graph

`graph.json` is networkx node-link: `nodes[]` and `links[]` (older `--no-cluster`
builds call the latter `edges[]`; the recipes below accept either via
`(.links // .edges)`).

- **node**: `id`, `label` (e.g. `Message`, `respond()`), `source_file`, `community`, `file_type`.
- **link**: `source`, `target` (node ids), `relation`, `confidence` (`EXTRACTED` | `INFERRED`), `weight`.
- **relations**: `calls`, `uses`, `references`, `imports`, `imports_from`, `inherits`, `extends`, `method`, `defines`, `contains`.

Two rules that keep the signals honest:

- **Ignore `contains`** for architectural signal — it's structural nesting
  (file→symbol, JSON key→value), not a dependency.
- **Exclude test files** from "problem" framing — tests legitimately have many
  members and zero inbound callers; that's not shallowness.

Start with `GRAPH_REPORT.md` for orientation (its **God Nodes** section is the
fan-in signal below, pre-computed). Drop to these recipes for targeted questions.

## Signals → ICA vocabulary

### Earning its keep (high fan-in)

Many modules depend on this one. The deletion test will likely say "complexity
reappears across N callers" — a candidate **deep** module. The opposite of a
deletion target.

```bash
jq -r '(.links // .edges) as $e
  | [$e[] | select(.relation|IN("calls","uses","references","method","inherits","extends"))]
  | group_by(.target) | map({node:.[0].target, fan_in:length})
  | sort_by(-.fan_in) | .[0:15][] | "\(.fan_in)\t\(.node)"' graphify-out/graph.json
```

### Shallow module (wide surface, thin use)

A module exposing a lot of surface (members) that few callers actually lean on —
**interface nearly as complex as the implementation**. Worth the deletion test:
does it concentrate complexity, or just relay it? Tests excluded; needs surface ≥ 3
to be worth asking about.

```bash
jq -r '(.links // .edges) as $e
  | (reduce ($e[]|select(.relation|IN("contains","defines","method"))) as $x ({}; .[$x.source]+=1)) as $surface
  | (reduce ($e[]|select(.relation|IN("calls","uses","references","imports","imports_from"))) as $x ({}; .[$x.target]+=1)) as $fanin
  | [ .nodes[]
      | select(.label == (.source_file | split("/") | last))
      | select((.source_file|test("(^|/)tests?/|(^|/)__tests__/|_test\\.|\\.test\\.|\\.spec\\."))|not)
      | {file:.source_file, surface:($surface[.id]//0), inbound:($fanin[.id]//0)} ]
  | map(select(.surface>=3)) | sort_by(.inbound,(-.surface)) | .[0:10][]
  | "\(.surface) surface / \(.inbound) inbound\t\(.file)"' graphify-out/graph.json
```

Language-agnostic: a *file* node is one whose `label` is the basename of its
`source_file` (`brain.py`, `handler.go`, `api.ts`), which excludes symbol nodes
without hardcoding an extension. The test filter drops `tests/`, `__tests__/`,
`_test.`, `.test.`, and `.spec.` conventions across languages.

### Pass-through (deletion-test candidate)

Exactly one thing in, one thing out. Classic relay: deleting it just moves the
edge. The deletion test usually says "complexity vanishes."

```bash
jq -r '(.links // .edges) as $e0 | [$e0[]|select(.relation!="contains")] as $e
  | (reduce $e[] as $x ({}; .[$x.target]+=1)) as $din
  | (reduce $e[] as $x ({}; .[$x.source]+=1)) as $dout
  | [ .nodes[] | select(.file_type=="code")
      | select(($din[.id]//0)==1 and ($dout[.id]//0)==1) | .label ]
  | "pass-through candidates: \(length)", .[]' graphify-out/graph.json
```

### Leaky seam (tight coupling between two files)

Many edges crossing between two files = a weak seam, behaviour bleeding across an
interface. A candidate for consolidation, or for a sharper seam between them.
(Test↔source pairs will appear — those are expected; look at the source↔source
pairs.)

```bash
jq -r '(reduce .nodes[] as $n ({}; .[$n.id]=$n.source_file)) as $f
  | [ (.links // .edges)[]
      | select(.relation|IN("calls","uses","imports","imports_from","references","inherits","extends"))
      | {a:$f[.source], b:$f[.target]} | select(.a and .b and .a!=.b)
      | ([.a,.b]|sort|join("  <->  ")) ]
  | group_by(.) | map({pair:.[0], edges:length})
  | sort_by(-.edges) | .[0:12][] | "\(.edges)\t\(.pair)"' graphify-out/graph.json
```

## Caveats

- **`INFERRED` edges are guesses** (graphify's heuristic, `weight` 0.8). Treat a
  signal resting mostly on inferred edges with extra suspicion — check `confidence`.
- **Doc-heavy / thin-code repos** produce a sparse graph dominated by `contains`.
  The signals get weak; fall back to organic exploration.
- **The graph can be stale.** If it predates recent edits, re-run map-the-codebase
  or discount accordingly.
- Recipes depend on graphify's `graph.json` shape. If a graphify upgrade changes
  field names, these rot silently — re-validate against a fresh graph.
