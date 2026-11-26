#!/usr/bin/env python3
"""import_tsv.py — 台帳を検証・正規化して実行キューに積み、順に回す。

矯正内容は必ずログに出す。黙って直さない。
実行に成功した行だけを使用済みにし、キューにも積む。

usage:
    python3 scripts/import_tsv.py config/catalog_nsfw.tsv --dry-run
    python3 scripts/import_tsv.py config/catalog_nsfw.tsv --count 1 --mark-used
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
SLUGS_FILE = ROOT / "config" / "slugs.txt"

FRAMING_PRIMARY = ("cowboy shot", "upper body", "close-up", "pov")
FRAMING_SECOND = ("from below", "from above", "over the shoulder", "mirror reflection")
ALLOWED_EXPR = ("expressionless", "shy", "pleasure", "smug")
MAX_INSTRUCTION_WORDS = 45
MAX_CONCEPT_CHARS = 120
MIN_CONCEPT_CHARS = 10
MAX_TITLE_CHARS = 40
EXPR_HISTORY = 3

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-\u00c0-\u024f]*")
SPACE_RE = re.compile(r"\s+")
SLUG_RE = re.compile(r"[^a-z0-9]+")
BLUSH_RE = re.compile(r"\bblush\w*\b(?!\s+pink)", re.I)
OCCLUDER_RE = re.compile(r"\b(quilt|blanket|sheet|curtain|duvet|towel)\b", re.I)
MOVE_RE = re.compile(r"\b(lift|lifted|pull|pulled|kick|kicked|open|opened|aside|down|bunch)\b", re.I)
DOUBLE_COMMA_RE = re.compile(r"\s*,\s*(?:,\s*)+")


# ------------------------------------------------------------------ helpers

def load_slugs() -> set:
    if not SLUGS_FILE.exists():
        return set()
    return {l.strip() for l in SLUGS_FILE.read_text(encoding="utf-8-sig").splitlines()
            if l.strip() and not l.startswith("#")}


def snap_slug(p: str, slugs: set) -> tuple:
    if not slugs or p in slugs:
        return p, []
    toks = set(p.split("_"))
    scored = []
    for s in sorted(slugs):
        sc = len(toks & set(s.split("_")))
        if sc >= 2:
            scored.append((sc, s))
    if not scored:
        return p, [f"place辞書外 {p}"]
    scored.sort(key=lambda x: (-x[0], x[1]))
    best = scored[0][1]
    return best, [f"place辞書補正 {p}->{best}"]


def truncate_tags(ins: str, max_words: int) -> tuple:
    """タグ境界で切る。from below を from で切らない。"""
    tags = [t.strip() for t in ins.split(",") if t.strip()]
    kept, total = [], 0
    for t in tags:
        n = len(TOKEN_RE.findall(t))
        if kept and total + n > max_words:
            return ", ".join(kept), True
        kept.append(t)
        total += n
    return ", ".join(kept), False


def normalize_fields(ins: str, mot: str) -> tuple:
    fixes = []
    if "camera locked" in ins:
        ins = ins.replace("camera locked", "")
        fixes.append("instructionからcamera locked除去")
    ins = re.sub(r"\bupper body focus\b", "upper body", ins)
    ins = re.sub(r"\bfull body\b", "cowboy shot", ins)
    ins = re.sub(r"\bfrom front\b", "", ins)

    tags = [t.strip() for t in ins.split(",") if t.strip()]
    prim = [t for t in tags if t in FRAMING_PRIMARY]
    if prim:
        head = prim[0]
        tags = [t for t in tags if t not in FRAMING_PRIMARY]
        tags.insert(0, head)
    sec = [t for t in tags if t in FRAMING_SECOND][:1]
    tags = [t for t in tags if t not in FRAMING_SECOND] + sec

    has_ins = any("inserted" in t for t in tags)
    has_cum = any(("creampie" in t or "cum overflow" in t) for t in tags)
    if has_ins and has_cum:
        tags = [t for t in tags if "inserted" not in t]
        fixes.append("penis inserted除去(creampieと競合)")

    tags = list(dict.fromkeys(tags))
    ins = DOUBLE_COMMA_RE.sub(", ", ", ".join(tags)).strip(" ,")

    mtags = [t.strip() for t in mot.split(",") if t.strip()]
    before = len(mtags)
    mtags = [t for t in mtags if t not in tags and t != "camera locked"]
    if len(mtags) != before:
        fixes.append("motion重複除去")
    mtags.append("camera locked")
    mot = DOUBLE_COMMA_RE.sub(", ", ", ".join(dict.fromkeys(mtags))).strip(" ,")
    return ins, mot, fixes


def sanitize(place, title, concept, instruction, motion, expression,
             recent_expr: tuple = (), slugs: set = frozenset()) -> tuple:
    fixes: list[str] = []

    p = SLUG_RE.sub("_", place.strip().lower()).strip("_") or "misc"
    p, f = snap_slug(p, slugs)
    fixes.extend(f)

    t = SPACE_RE.sub(" ", title.replace("|", "/")).strip()
    if len(t) > MAX_TITLE_CHARS:
        t = t[:MAX_TITLE_CHARS]
        fixes.append("title短縮")
    if not t:
        t = "無題"
        fixes.append("title補完")

    c = SPACE_RE.sub(" ", concept.replace("|", "/")).strip()
    if "赤面" in c or BLUSH_RE.search(c):
        c = c.replace("赤面", "")
        c = BLUSH_RE.sub("", c)
        c = SPACE_RE.sub(" ", c).strip(" 、。,")
        fixes.append("赤面除去")
    if len(c) > MAX_CONCEPT_CHARS:
        c = c[:MAX_CONCEPT_CHARS].rstrip(" 、。,")
        fixes.append("concept短縮")

    ins = SPACE_RE.sub(" ", instruction).strip().lower()
    mot = SPACE_RE.sub(" ", motion).strip().lower()
    ins, mot, f = normalize_fields(ins, mot)
    fixes.extend(f)

    if not any(ins.startswith(x) for x in FRAMING_PRIMARY):
        ins = "cowboy shot, " + ins
        fixes.append("構図タグ補完")

    if len(TOKEN_RE.findall(ins)) > MAX_INSTRUCTION_WORDS:
        ins, cut = truncate_tags(ins, MAX_INSTRUCTION_WORDS)
        if cut:
            fixes.append("instruction短縮")

    ex = expression.strip().lower()
    if ex not in ALLOWED_EXPR:
        pool = [e for e in ALLOWED_EXPR if e not in recent_expr] or list(ALLOWED_EXPR)
        new = random.choice(pool)
        fixes.append(f"表情矯正 {expression!r}->{new!r}")
        ex = new
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
    if not linenos:
        return
    lines = path.read_text(encoding="utf-8-sig").splitlines()
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


# --------------------------------------------------------------------- main

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
    if args.count < 1:
        print("❌ --count は1以上")
        return 2
    if args.interval < 0:
        print("❌ --interval が負")
        return 2
    if args.end and args.start > args.end:
        print(f"❌ --start {args.start} > --end {args.end}")
        return 2

    slugs = load_slugs()
    if not slugs:
        print("⚠️ config/slugs.txt が空。place補正なしで続行")

    rows: list[tuple[int, list[str]]] = []
    recent: list[str] = []
    skipped = 0

    with args.path.open(encoding="utf-8-sig") as f:
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

            *vals, fixes = sanitize(*parts[:6],
                                    recent_expr=tuple(recent[-EXPR_HISTORY:]),
                                    slugs=slugs)
            if fixes:
                print(f"[fix] {lineno}行目: {', '.join(fixes)}")
            print(f"[ok ] {lineno}行目: {vals[0]} / {vals[5]} / {vals[1]}")
            recent.append(vals[5])
            rows.append((lineno, vals))

    if not rows:
        print(f"取り込める行が無い（除外 {skipped}）")
        return 1

    print(f"--- 候補 {len(rows)} / 除外 {skipped} ---")

    if args.dry_run:
        for _, r in rows:
            print("|".join(r))
        print("\n[dry-run] 実行コマンド例:")
        print(" ".join(f'"{x}"' if " " in x else x for x in build_cmd(rows[0][1])))
        return 0

    target = rows[:args.count]
    if len(target) < len(rows):
        print(f"[note] 候補 {len(rows)} のうち {len(target)} 件だけ実行（残りは未使用のまま）")

    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    done = 0
    done_linenos: set[int] = set()

    for i, (lineno, r) in enumerate(target, 1):
        print(f"\n===== {i}/{len(target)} : {r[1]} =====")
        rc = subprocess.run(build_cmd(r)).returncode
        if rc != 0:
            print(f"⚠️ 終了コード {rc}（未使用のまま継続）")
            continue
        done += 1
        done_linenos.add(lineno)
        with QUEUE.open("a", encoding="utf-8") as q:
            q.write("|".join(r) + "\n")
        if i < len(target):
            time.sleep(args.interval)

    print(f"\n完了 {done}/{len(target)}")
    if args.mark_used:
        mark_used(args.path, done_linenos)
        print(f"[mark] 成功した {len(done_linenos)} 行のみ使用済みに")
    return 0 if done else 3


if __name__ == "__main__":
    sys.exit(main())
