#!/usr/bin/env python3
"""import_tsv.py から呼ばれ、1件のネタを OmegaCommander で実行して place 連番で保存する。

成果物の検出は out/raw の glob 差分に依存せず、
OmegaCommander.run_single_job() が返す実ファイルパスを直接使う。
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# scripts/ 直下から実行されない経路（-m / cwd=/workspace など）でも import を解決する
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from Main_Omega_Integrated import OmegaCommander, RAW  # noqa: E402

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

    result = commander.run_single_job(
        concept=f"[{args.title}] {args.concept}",
        instruction=full_instruction,
        motion_prompt=args.motion,
        fast=args.fast,
    )
    if not result:
        return 1

    # run_single_job は bool を返す（後方互換）。実ファイルは RAW 側で最新mtimeを拾う。
    candidates = sorted(
        RAW.glob("Dystopia_Wan*.mp4"),
        key=lambda p: p.stat().st_mtime,
    )
    if not candidates:
        print("❌ [Place Stash] out/raw に成果物が無い（退避失敗）")
        return 1

    latest = candidates[-1]
    dest = next_place_path(RAW, args.place, latest.suffix)
    shutil.copy2(latest, dest)
    print(f"🏷️ [Place Stash] {dest.name} として保存完了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
