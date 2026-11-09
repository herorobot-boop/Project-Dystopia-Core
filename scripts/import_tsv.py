#!/usr/bin/env python3
"""data/catalog.tsv を data/scenarios/<engine>_<place>/<id>.yaml に変換する。

同じidが既にあれば上書きする。台帳が唯一の正であり、YAMLは生成物。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.tsv"
OUT_DIR = ROOT / "data" / "scenarios"

COLUMNS = [
    "id", "title", "engine", "place", "tags", "female", "male",
    "wardrobe_female", "wardrobe_male", "props", "beats", "prompt_seed", "notes",
]

SPLIT_RE = re.compile(r"[、,;|]")


def slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:30] or "place"


def split_multi(text: str) -> list[str]:
    return [part.strip() for part in SPLIT_RE.split(text or "") if part.strip()]


def build_record(row: dict[str, str]) -> dict:
    engine = row["engine"].strip()
    place_slug = slug(row["place"])
    rid = row["id"].strip() or f"{engine.lower()}_{place_slug}_000"

    record = {
        "id": rid,
        "title": row["title"].strip(),
        "engine": engine,
        "place": row["place"].strip(),
        "tags": split_multi(row["tags"]),
        "cast": {
            "female": int(row["female"] or 1),
            "male": int(row["male"] or 0),
            "cast_note": "",
        },
        "wardrobe": {
            "female": split_multi(row["wardrobe_female"]),
            "male": split_multi(row["wardrobe_male"]),
        },
        "key_props": split_multi(row["props"]),
        "beats": split_multi(row["beats"]),
        "verdicts": {"V1": "段階触診", "V3": "観察"},
        "prompt_seed": " ".join(row["prompt_seed"].split()),
        "ng": ["blush", "mannequin"],
        "notes": row["notes"].strip(),
    }
    return record


def dump_yaml(record: dict) -> str:
    return yaml.safe_dump(
        record,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )


def main() -> int:
    if not CATALOG.exists():
        print(f"台帳がない: {CATALOG}", file=sys.stderr)
        return 1

    lines = CATALOG.read_text(encoding="utf-8").splitlines()
    if not lines:
        print("台帳が空", file=sys.stderr)
        return 1

    header = lines[0].split("\t")
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        print(f"ヘッダに列がない: {missing}", file=sys.stderr)
        return 1

    index = {name: header.index(name) for name in COLUMNS}
    written = 0

    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        row = {name: cells[index[name]] for name in COLUMNS}

        if not row["title"].strip():
            print(f"  {lineno}行目: titleが空。飛ばす")
            continue

        record = build_record(row)
        target_dir = OUT_DIR / f"{record['engine'].lower()}_{slug(record['place'])}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{record['id']}.yaml"
        target.write_text(dump_yaml(record), encoding="utf-8")
        print(f"  書き出し: {target.relative_to(ROOT)}")
        written += 1

    print(f"\n完了: {written} 件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
