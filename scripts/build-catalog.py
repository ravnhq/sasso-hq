#!/usr/bin/env python3
"""Generate hq-core/catalog.json from skill frontmatter + taxonomy.yml.

Scans every plugins/*/skills/*/SKILL.md, validates each first-party skill is
tagged in taxonomy.yml with tags drawn from the locked vocab, and writes the
catalog the recommend-workflow skill reads. Run via pre-commit; CI checks freshness.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TAXONOMY = ROOT / "plugins" / "hq-core" / "taxonomy.yml"
CATALOG = ROOT / "plugins" / "hq-core" / "catalog.json"
PLUGINS = ROOT / "plugins"


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text()
    if not text.startswith("---"):
        raise ValueError(f"{skill_md}: missing frontmatter")
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm)


def build() -> tuple[list, list]:
    tax = yaml.safe_load(TAXONOMY.read_text())
    vocab = set(tax["vocab"])
    skill_tags = tax["skills"]
    errors = []
    entries = []

    for skill_md in sorted(PLUGINS.glob("*/skills/*/SKILL.md")):
        plugin = skill_md.parents[2].name
        fm = frontmatter(skill_md)
        name = fm["name"]
        if name not in skill_tags:
            errors.append(f"{name} ({plugin}): not in taxonomy.yml `skills`")
            continue
        tags = skill_tags[name]
        bad = set(tags) - vocab
        if bad:
            errors.append(f"{name}: tags not in vocab: {sorted(bad)}")
        entries.append({
            "name": name,
            "plugin": plugin,
            "source": "hq",
            "description": fm["description"],
            "tags": tags,
            "install": f"claude plugin install {plugin}@hq",
        })

    catalogued = {e["name"] for e in entries}
    for name in skill_tags:
        if name not in catalogued:
            errors.append(f"taxonomy lists `{name}` but no SKILL.md found for it")

    for name, meta in tax.get("external", {}).items():
        bad = set(meta["tags"]) - vocab
        if bad:
            errors.append(f"external {name}: tags not in vocab: {sorted(bad)}")
        entries.append({
            "name": name,
            "plugin": meta["plugin"],
            "source": "external",
            "description": meta["description"],
            "tags": meta["tags"],
            "install": f"claude plugin install {meta['plugin']}",
        })

    return entries, errors


def main() -> int:
    entries, errors = build()
    if errors:
        print("catalog build failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    CATALOG.write_text(json.dumps({"skills": entries}, indent=2) + "\n")
    print(f"wrote {CATALOG.relative_to(ROOT)} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
