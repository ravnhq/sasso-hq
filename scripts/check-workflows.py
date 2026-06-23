#!/usr/bin/env python3
"""Validate that workflow playbooks only reference skills that exist.

Convention: each plugins/hq-core/workflows/*.md carries frontmatter with a
`skills:` list naming the skills its path uses. Every name must appear in the
generated catalog (first-party or external). No-op until Phase 3 adds playbooks.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / "plugins" / "hq-core" / "workflows"
CATALOG = ROOT / "plugins" / "hq-core" / "catalog.json"


def main() -> int:
    if not WORKFLOWS.exists():
        print("no workflows/ yet — nothing to check")
        return 0
    known = {s["name"] for s in json.loads(CATALOG.read_text())["skills"]}
    errors = []
    for md in sorted(WORKFLOWS.glob("*.md")):
        text = md.read_text()
        if not text.startswith("---"):
            errors.append(f"{md.name}: missing frontmatter with `skills:`")
            continue
        fm = yaml.safe_load(text.split("---", 2)[1])
        for name in fm.get("skills", []):
            if name not in known:
                errors.append(f"{md.name}: references unknown skill `{name}`")
    if errors:
        print("workflow check failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("workflow playbooks ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
