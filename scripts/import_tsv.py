#!/usr/bin/env python3
"""import_tsv.py — 台帳を検証・正規化して実行キューに積み、順に回す。

モデル出力は仕様を守らない。ここで実行時に矯正し、
「壊れた行を落とす」のではなく「使える形に直してから積む」。
矯正内容は必ずログに出す。黙って直さない。

usage:
    python3 scripts/import_tsv.py config/catalog_nsfw.tsv --dry-run
    python3 scripts/import_tsv.py config/catalog_nsfw.tsv --count 1
    python3 scripts/import_tsv.py config/catalog_nsfw.tsv --start 1 --end 3 --count 3
"""
from __future__ import annotations

import argparse
import random
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "out" / "queue.tsv"
GEN = ROOT / "scripts" / "gen.py"

FRAMING = ("cowboy shot", "upper body", "close-up", "from below", "from above", "pov")
ALLOWED_EXPR = ("expressionless", "shy", "pleasure", "smug")
MAX_INSTRUCTION_WORDS = 45
MAX_CONCEPT_CHARS = 120
MIN_CONCEPT_CHARS = 15
MAX_TITLE_CHARS = 40
EXPR_HISTORY = 3

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-\u00c0-\u024f]*")
SPACE_RE = re.compile(r"\s+")
SLUG_RE = re.compile(r"[^a-z0-9]+")
BLUSH_RE = re.compile(r"\bblush\w*\b", re.I)
OCCLUDER_RE = re.compile(r"\b(quilt|blanket|sheet|curtain|duvet|towel)\b", re.I)
MOVE_RE = re.compile(r"\b(lift|lifted|pull|pulled|kick|kicked|open|opened|aside|down|bunch)\b", re.I)


def sanitize(place, title, concept, instruction, motion, expression,
             recent_expr: tuple = ()) -> tuple:
    fixes: list[str] = []

    p = SLUG_RE.sub("_", place.strip().lower()).strip("_") or "misc"
    if p != place.strip():
        fixes.append(f"place矯正 {place!r}->{p!r}")

    t = SPACE_RE.sub(" ", title).strip()
    if len(t) > MAX_TITLE_CHARS:
        t = t[:MAX_TITLE_CHARS]
        fixes.append("title短縮")
    if not t:
        t = "無題"
        fixes.append("title補完")

    c = SPACE_RE.sub(" ", concept).strip()
    if "赤面" in c or BLUSH_RE.search(c):
        c = c.replace("赤面", "")
        c = BLUSH_RE.sub("", c)
        c = SPACE_RE.sub(" ", c).strip(" 、。,")
        fixes.append("赤面除去")
    if len(c) > MAX_CONCEPT_CHARS:
        c = c[:MAX_CONCEPT_CHARS].rstrip(" 、。,")
        fixes.append("concept短縮")

    ins = SPACE_RE.sub(" ", instruction).strip().lower()
    if not any(f in ins for f in FRAMING):
        ins = "cowboy shot, " + ins
        fixes.append("構図タグ補完")
    if len(TOKEN_RE.findall(ins)) > MAX_INSTRUCTION_WORDS:
        ins = " ".join(ins.split()[:MAX_INSTRUCTION_WORDS]).rstrip(",; ")
        fixes.append("instruction短縮")
    ins = ins.rstrip(",; ")

    mot = SPACE_RE.sub(" ", motion).strip().lower()
    if "camera locked" not in mot:
        mot = (mot.rstrip(", ") + ", camera locked").lstrip(", ")
        fixes.append("camera locked補完")

    ex = expression.strip().lower()
    if ex not in ALLOWED_EXPR:
        pool = [e for e in ALLOWED_EXPR if e not in recent_expr] or list(ALLOWED_EXPR)
        ex = random.choice(pool)
        fixes.append(f"表情矯正 {expression!r}->{ex!r}")
    elif ex in recent_expr and len(recent_expr) >= EXPR_HISTORY:
        pool = [e for e in ALLOWED_EXPR if e not in recent_expr]
        if pool:
            new = random.choice(pool)
            fixes.append(f"表情重複回避 {ex}->{new}")
            ex = new

    if OCCLUDER_RE.search(ins) and not MOVE_RE.search(ins):
        fixes.append("遮蔽物が退いていない疑い")

    return p, t, c, ins, mot, ex, fixes


def parse_line(line: str):
    sep = "\t" if "\t" in line else "|"
    if line.lower().startswith(f"place{sep}".lower()):
        return None, sep
    return [x.strip() for x in line.split(sep)], sep


def build_cmd(row) -> list[str]:
    place, title, concept, instruction, motion, expression = row
    return [sys.executable, str(GEN),
            "--place", place, "--title", title, "--concept", concept,
            "--instruction", instruction, "--motion", motion,
            "--expression", expression]


def mark_used(path: Path, linenos: set[int]):
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        if i not in linenos:
            continue
        sep = "\t" if "\t" in line else "|"
        parts = line.split(sep)
        if len(parts) < 7:
            lines[i - 1] = line + f"{sep}1"
        else:
            parts[6] = "1"
            lines[i - 1] = sep.join(parts)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--interval", type=int, default=15)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=0)
    ap.add_argument("--mark-used", action="store_true")
    args = ap.parse_args()

    if not args.path.exists():
        print(f"❌ 入力が無い: {args.path}")
        return 2
    if not GEN.exists():
        print(f"❌ gen.py が無い: {GEN}")
        return 2

    rows, recent, used_linenos = [], [], set()
    skipped = 0

    with args.path.open(encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n").rstrip("\r")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if lineno < args.start or (args.end and lineno > args.end):
                continue

            parts, sep = parse_line(line)
            if parts is None:
                continue
            if len(parts) < 6:
                print(f"[skip] {lineno}行目: 列不足({len(parts)})")
                skipped += 1
                continue
            if len(parts) > 6 and parts[6] == "1":
                print(f"[skip] {lineno}行目: 使用済み")
                skipped += 1
                continue
            if len(parts[2]) < MIN_CONCEPT_CHARS:
                print(f"[skip] {lineno}行目: conceptが短すぎる")
                skipped += 1
                continue

            row = sanitize(*parts[:6], recent_expr=tuple(recent[-EXPR_HISTORY:]))
            *vals, fixes = row
            if fixes:
                print(f"[fix] {lineno}行目: {', '.join(fixes)}")
            print(f"[ok ] {lineno}行目: {vals[0]} / {vals[5]} / {vals[1]}")
            recent.append(vals[5])
            rows.append(vals)
            used_linenos.add(lineno)

    if not rows:
        print("取り込める行が無い")
        return 1

    print(f"--- 候補 {len(rows)} / 除外 {skipped} ---")

    if args.dry_run:
        for r in rows:
            print("|".join(r))
        print("\n[dry-run] 実行コマンド例:")
        print(" ".join(f'"{x}"' if " " in x else x for x in build_cmd(rows[0])))
        return 0

    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE.open("a", encoding="utf-8") as q:
        for r in rows:
            q.write("|".join(r) + "\n")
    print(f"[queue] 追記: {QUEUE}")

    done = 0
    for i, r in enumerate(rows[:args.count], 1):
        print(f"\n===== {i}/{min(args.count, len(rows))} : {r[1]} =====")
        rc = subprocess.run(build_cmd(r)).returncode
        if rc != 0:
            print(f"⚠️ 終了コード {rc}（続行）")
        else:
            done += 1
        if i < args.count:
            time.sleep(args.interval)

    print(f"\n完了 {done}/{min(args.count, len(rows))}")
    if args.mark_used and done:
        mark_used(args.path, used_linenos)
        print("[mark] 台帳に使用済み印を付与")
    return 0


if __name__ == "__main__":
    sys.exit(main())
