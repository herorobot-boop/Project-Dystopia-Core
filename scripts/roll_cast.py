#!/usr/bin/env python3
"""config/cast.yaml から女優を抽選して1行で出す。"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "config" / "cast.yaml"


def weighted(entries: list[dict]) -> str:
    values = [str(e["value"]) for e in entries]
    weights = [int(e.get("weight", 1)) for e in entries]
    return random.choices(values, weights=weights, k=1)[0]


def main() -> int:
    if not CONF.exists():
        print("config/cast.yaml がない", file=sys.stderr)
        return 1

    conf = yaml.safe_load(CONF.read_text(encoding="utf-8")) or {}
    female = conf.get("female", {})
    male = conf.get("male", {})

    nationality = weighted(female.get("nationality", [{"value": "japanese", "weight": 1}]))
    age = random.randint(int(female.get("age_min", 20)), int(female.get("age_max", 38)))
    cup = weighted(female.get("cup", [{"value": "E", "weight": 1}]))
    hair = weighted(female.get("hair", [{"value": "black hair", "weight": 1}]))
    expression = weighted(female.get("expression", [{"value": "deadpan", "weight": 1}]))
    skin = female.get("skin", "even skin tone, no blush")

    male_age = random.randint(int(male.get("age_min", 22)), int(male.get("age_max", 55)))
    male_build = weighted(male.get("build", [{"value": "average build", "weight": 1}]))

    woman = f"{nationality} woman, {age} years old, {cup} cup, {hair}, {expression}, {skin}"
    man = f"{nationality if nationality == 'japanese' else 'japanese'} man, {male_age} years old, {male_build}"

    print("--- female ---")
    print(woman)
    print("--- male ---")
    print(man)
    print("\n# 上の2行をYAMLの cast.cast_note に1行で貼る:")
    print(f"{woman}, with {man}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
