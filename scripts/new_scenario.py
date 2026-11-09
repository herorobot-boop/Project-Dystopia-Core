#!/usr/bin/env python3
"""1件だけ雛形を作る。--engine E2 --place menstoi --title "..." """
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCEN_DIR = ROOT / "data" / "scenarios"
TEMPLATE = SCEN_DIR / "_template.yaml"


def slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:30] or "place"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", required=True, choices=["E1", "E2", "E3", "E4"])
    parser.add_argument("--place", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()

    if not TEMPLATE.exists():
        print("_template.yaml がない", file=sys.stderr)
        return 1

    place_slug = slug(args.place)
    target_dir = SCEN_DIR / f"{args.engine.lower()}_{place_slug}"
    target_dir.mkdir(parents=True, exist_ok=True)

    seq = 1
    while (target_dir / f"{args.engine.lower()}_{place_slug}_{seq:03d}.yaml").exists():
        seq += 1

    rid = f"{args.engine.lower()}_{place_slug}_{seq:03d}"
    target = target_dir / f"{rid}.yaml"

    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("id: e2_place_000", f"id: {rid}")
    text = text.replace("title: 仮タイトル", f"title: {args.title}")
    text = text.replace("engine: E2", f"engine: {args.engine}")
    text = text.replace("place: 仮の場所", f"place: {args.place}")

    target.write_text(text, encoding="utf-8")
    print(f"作成: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
