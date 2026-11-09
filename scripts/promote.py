#!/usr/bin/env python3
"""out/raw の連番を out/selected / out/rejected に振り分ける。

使い方:
  python3 promote.py 3 7 12          # 3,7,12 を selected へ
  python3 promote.py --reject 4 9    # 4,9 を rejected へ
  python3 promote.py --list          # 現状を表示
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "out" / "raw"
SEL = ROOT / "out" / "selected"
REJ = ROOT / "out" / "rejected"

EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def ensure_dirs() -> None:
    for d in (RAW, SEL, REJ):
        d.mkdir(parents=True, exist_ok=True)


def find_by_number(number: int) -> Path | None:
    for path in sorted(RAW.iterdir()):
        if path.suffix.lower() not in EXTS:
            continue
        stem = path.stem
        if stem.isdigit() and int(stem) == number:
            return path
    return None


def move(number: int, dest: Path) -> None:
    src = find_by_number(number)
    if src is None:
        print(f"  {number}: raw に無い")
        return
    target = dest / src.name
    if target.exists():
        print(f"  {number}: {dest.name} に既にある")
        return
    shutil.move(str(src), str(target))
    print(f"  {number}: → {dest.name}/{src.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="*", type=int)
    parser.add_argument("--reject", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    ensure_dirs()

    if args.list:
        for d in (RAW, SEL, REJ):
            names = sorted(p.name for p in d.iterdir() if p.suffix.lower() in EXTS)
            print(f"{d.name}: {len(names)} 件")
            for name in names[:20]:
                print(f"  {name}")
        return 0

    if not args.numbers:
        parser.print_help()
        return 1

    dest = REJ if args.reject else SEL
    for number in args.numbers:
        move(number, dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
