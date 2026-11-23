#!/usr/bin/env python3
"""import_tsv.py から呼び出され、1件のネタを OmegaCommander で実行して place 連番で保存する。"""
import argparse
import shutil
import sys
from pathlib import Path

from Main_Omega_Integrated import OmegaCommander, RAW

EXPR_MAP = {
    "expressionless": "expressionless, calm stoic face, neutral gaze",
    "shy": "shy expression, embarrassed, averted gaze, hesitant",
    "pleasure": "pleasure expression, parted lips, half-closed eyes, trembling",
    "smug": "smug expression, confident smirk, teasing gaze",
}


def next_place_path(directory: Path, place: str, ext: str = ".mp4") -> Path:
    idx = 1
    while True:
        candidate = directory / f"{place}_{idx:02d}{ext}"
        if not candidate.exists():
            return candidate
        idx += 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--place", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--concept", required=True)
    ap.add_argument("--instruction", required=True)
    ap.add_argument("--motion", required=True)
    ap.add_argument("--expression", required=True)
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()

    expr_tags = EXPR_MAP.get(args.expression.lower(), args.expression)
    full_instruction = f"{args.instruction}, {expr_tags}"

    commander = OmegaCommander()
    if not commander.bridge.wait_until_ready():
        print("❌ ComfyUIが起動していません")
        return 1

    before = set(RAW.glob("Dystopia_Wan*.mp4"))
    ok = commander.run_single_job(
        concept=f"[{args.title}] {args.concept}",
        instruction=full_instruction,
        motion_prompt=args.motion,
        fast=args.fast,
    )
    if not ok:
        return 1

    after = sorted(set(RAW.glob("Dystopia_Wan*.mp4")) - before, key=lambda p: p.stat().st_mtime)
    if after:
        latest = after[-1]
        dest = next_place_path(RAW, args.place, latest.suffix)
        shutil.copy2(latest, dest)
        print(f"🏷️ [Place Stash] {dest.name} として保存完了")

    return 0


if __name__ == "__main__":
    sys.exit(main())
