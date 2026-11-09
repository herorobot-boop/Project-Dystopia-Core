#!/usr/bin/env python3
"""YAMLから dist/blocks/<engine>/<id>.md と dist/INDEX.md を生成する。"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCEN_DIR = ROOT / "data" / "scenarios"
STYLE_PATH = ROOT / "config" / "style.yaml"
DIST = ROOT / "dist"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def flatten(items) -> str:
    return ", ".join(str(x) for x in items if str(x).strip())


def compose(record: dict, style: dict, camera_rules: dict):
    parts: list[str] = []

    parts.append(record.get("place", ""))

    cast = record.get("cast", {})
    note = cast.get("cast_note", "").strip()
    if note:
        parts.append(note)

    wardrobe = record.get("wardrobe", {})
    female_clothes = wardrobe.get("female", [])
    if female_clothes:
        parts.append("wearing " + flatten(female_clothes))

    props = record.get("key_props", [])
    if props:
        parts.append(flatten(props))

    parts.append(record.get("prompt_seed", "").strip())

    tags = record.get("tags", [])
    if tags:
        parts.append(flatten(tags))

    guard = style.get("positive_guard", "").strip()
    if guard:
        parts.append(guard)

    suffix = style.get("positive_suffix", "").strip()
    if suffix:
        parts.append(suffix)

    positive = ", ".join(p for p in parts if p)

    negative_items = list(style.get("default_ng", []))
    negative_items += record.get("ng", [])
    seen = set()
    negative_list = []
    for item in negative_items:
        key = str(item).lower()
        if key not in seen:
            seen.add(key)
            negative_list.append(str(item))
    negative = flatten(negative_list)

    camera = ""
    tag_set = set(tags)
    for key, rule in camera_rules.items():
        if key in tag_set:
            camera = rule
            break

    return positive, negative, camera


def main() -> int:
    if not SCEN_DIR.exists():
        print("YAMLフォルダがない", file=sys.stderr)
        return 1

    style = load_yaml(STYLE_PATH)
    camera_rules = style.get("camera_rules", {}) or {}

    files = sorted(p for p in SCEN_DIR.rglob("*.yaml") if p.name != "_template.yaml")
    if not files:
        print("YAMLが1件もない", file=sys.stderr)
        return 1

    DIST.mkdir(parents=True, exist_ok=True)
    index_rows: list[str] = []
    built = 0

    for path in files:
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            print(f"  飛ばす（マップでない）: {path}")
            continue

        rid = str(record.get("id", path.stem))
        engine = str(record.get("engine", "E2"))
        positive, negative, camera = compose(record, style, camera_rules)

        out_dir = DIST / "blocks" / engine.lower()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{rid}.md"

        body = [
            f"# {record.get('title', rid)}",
            "",
            f"- id: `{rid}`",
            f"- engine: {engine}",
            f"- place: {record.get('place', '')}",
            f"- tags: {flatten(record.get('tags', []))}",
            "",
            "## POSITIVE",
            "",
            "```",
            positive,
            "```",
            "",
            "## NEGATIVE（実CFG 2.0以上のときだけ効く）",
            "",
            "```",
            negative,
            "```",
            "",
        ]

        if camera:
            body += ["## 画角", "", camera, ""]

        beats = record.get("beats", [])
        if beats:
            body += ["## ビート（動画化するときの順序）", ""]
            for i, beat in enumerate(beats, start=1):
                body.append(f"{i}. {beat}")
            body.append("")

        verdicts = record.get("verdicts", {})
        if verdicts:
            body += ["## 判定機構", ""]
            for key, value in verdicts.items():
                body.append(f"- {key}: {value}")
            body.append("")

        notes = record.get("notes", "")
        if notes:
            body += ["## メモ", "", notes, ""]

        out_path.write_text("\n".join(body), encoding="utf-8")
        index_rows.append(
            f"| {rid} | {record.get('title', '')} | {engine} | {record.get('place', '')} |"
        )
        built += 1

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    index = [
        "# 生成索引",
        "",
        f"生成日時: {stamp}",
        f"件数: {built}",
        "",
        "| id | title | engine | place |",
        "|---|---|---|---|",
    ] + index_rows + [""]
    (DIST / "INDEX.md").write_text("\n".join(index), encoding="utf-8")
    (DIST / ".gitkeep").write_text("", encoding="utf-8")

    print(f"完了: {built} 件 → {DIST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
