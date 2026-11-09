#!/usr/bin/env python3
"""data/scenarios 配下のYAMLを検品する。1件でも駄目なら終了コード1。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCEN_DIR = ROOT / "data" / "scenarios"
STYLE = ROOT / "config" / "style.yaml"

ID_RE = re.compile(r"^[a-z0-9_]{3,48}$")
ENGINES = {"E1", "E2", "E3", "E4"}
VERDICT_KEYS = {"V1", "V2", "V3", "V4"}
REQUIRED = [
    "id", "title", "engine", "place", "tags",
    "cast", "wardrobe", "key_props", "beats", "verdicts", "prompt_seed",
]

MAX_PROMPT = 900
MAX_TAGS = 8
MIN_BEATS, MAX_BEATS = 4, 12
MIN_PROPS, MAX_PROPS = 1, 5
MIN_WARDROBE, MAX_WARDROBE = 1, 6

errors: list[str] = []
seen_ids: dict[str, Path] = {}


def fail(path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def check_list(path, record, key, min_len, max_len, item_max=None):
    value = record.get(key)
    if not isinstance(value, list):
        fail(path, f"{key} はリストで書く")
        return
    if not (min_len <= len(value) <= max_len):
        fail(path, f"{key} の要素数は {min_len}〜{max_len}（今 {len(value)}）")
    for item in value:
        if not isinstance(item, str):
            fail(path, f"{key} の要素に文字列以外がある")
        elif item_max and len(item) > item_max:
            fail(path, f"{key} の要素が長すぎる（{len(item)}字）: {item[:20]}")


def check_record(path: Path, record: dict, ng_default: list[str]) -> None:
    for key in REQUIRED:
        if key not in record:
            fail(path, f"必須キーがない: {key}")
    if errors and any(str(path.relative_to(ROOT)) in e and "必須キー" in e for e in errors):
        return

    rid = record.get("id", "")
    if not isinstance(rid, str) or not ID_RE.match(rid):
        fail(path, f"id の形式が違う（半角小文字・数字・_ のみ）: {rid!r}")
    elif rid in seen_ids and seen_ids[rid] != path:
        fail(path, f"id が重複: {rid}（{seen_ids[rid].relative_to(ROOT)}）")
    else:
        seen_ids[rid] = path

    if path.stem != rid and path.stem != "_template":
        fail(path, f"ファイル名と id が一致しない（{path.stem} / {rid}）")

    title = record.get("title", "")
    if not isinstance(title, str) or not (2 <= len(title) <= 60):
        fail(path, "title は2〜60文字")

    if record.get("engine") not in ENGINES:
        fail(path, f"engine は E1/E2/E3/E4 のどれか: {record.get('engine')!r}")

    place = record.get("place", "")
    if not isinstance(place, str) or not (2 <= len(place) <= 40):
        fail(path, "place は2〜40文字")

    check_list(path, record, "tags", 1, MAX_TAGS, item_max=20)
    check_list(path, record, "key_props", MIN_PROPS, MAX_PROPS, item_max=30)
    check_list(path, record, "beats", MIN_BEATS, MAX_BEATS, item_max=80)

    cast = record.get("cast")
    if not isinstance(cast, dict):
        fail(path, "cast はマップで書く")
    else:
        for key, low, high in (("female", 1, 3), ("male", 0, 3)):
            value = cast.get(key)
            if not isinstance(value, int):
                fail(path, f"cast.{key} は整数")
            elif not (low <= value <= high):
                fail(path, f"cast.{key} は {low}〜{high}")
        note = cast.get("cast_note", "")
        if isinstance(note, str) and len(note) > 200:
            fail(path, "cast_note が200字を超えている")

    wardrobe = record.get("wardrobe")
    if not isinstance(wardrobe, dict):
        fail(path, "wardrobe はマップで書く")
    else:
        check_list(path, wardrobe, "female", MIN_WARDROBE, MAX_WARDROBE, item_max=24)
        if "male" in wardrobe:
            check_list(path, wardrobe, "male", 0, MAX_WARDROBE, item_max=24)

    verdicts = record.get("verdicts")
    if not isinstance(verdicts, dict):
        fail(path, "verdicts はマップで書く")
    else:
        extra = set(verdicts) - VERDICT_KEYS
        if extra:
            fail(path, f"verdicts に未知のキー: {sorted(extra)}")
        if not verdicts:
            fail(path, "verdicts が空。V1〜V4のどれかを書く")

    prompt = record.get("prompt_seed", "")
    if not isinstance(prompt, str) or not (20 <= len(prompt) <= MAX_PROMPT):
        fail(path, f"prompt_seed は20〜{MAX_PROMPT}文字")

    ng = record.get("ng", [])
    if not isinstance(ng, list):
        fail(path, "ng はリスト")
    elif len(ng) > 10:
        fail(path, "ng は10件まで")

    merged_ng = {str(x).lower() for x in (ng or [])} | {x.lower() for x in ng_default}
    lowered = prompt.lower()
    if "blush" in merged_ng and "blush" in lowered and "no blush" not in lowered:
        fail(path, "prompt_seed に blush があるが no blush と書いていない")

    if "mannequin" not in lowered and "female" in cast and cast.get("male", 0) >= 1:
        pass


def main() -> int:
    if not SCEN_DIR.exists():
        print(f"フォルダがない: {SCEN_DIR}", file=sys.stderr)
        return 1

    ng_default: list[str] = []
    if STYLE.exists():
        style = yaml.safe_load(STYLE.read_text(encoding="utf-8")) or {}
        ng_default = [str(x) for x in style.get("default_ng", [])]

    files = sorted(SCEN_DIR.rglob("*.yaml"))
    if not files:
        print("YAMLが1件もない", file=sys.stderr)
        return 1

    for path in files:
        if path.name == "_template.yaml":
            continue
        try:
            record = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            fail(path, f"YAML構文エラー: {exc}")
            continue
        if not isinstance(record, dict):
            fail(path, "中身がマップではない")
            continue
        check_record(path, record, ng_default)

    if errors:
        print(f"NG {len(errors)} 件\n")
        for line in errors:
            print("  " + line)
        return 1

    print(f"OK {len(files) - (1 if (SCEN_DIR / '_template.yaml').exists() else 0)} 件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
