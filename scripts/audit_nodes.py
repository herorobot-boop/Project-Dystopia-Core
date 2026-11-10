#!/usr/bin/env python3
import json, re, sys, urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8188"
try:
    with urllib.request.urlopen(f"{BASE}/object_info", timeout=30) as r:
        known = set(json.load(r))
except Exception as e:
    print(f"[FATAL] ComfyUI に繋がらない: {e}"); sys.exit(2)

pat = re.compile(r'"class_type"\s*:\s*"([^"]+)"')
bad = {}
for p in sorted(Path("scripts").glob("*.py")):
    txt = p.read_text(errors="ignore")
    for m in set(pat.findall(txt)):
        if m not in known:
            bad.setdefault(m, []).append(p.name)

if not bad:
    print("[OK] 未定義ノードなし"); sys.exit(0)
print("[NG] 存在しないノード:")
for n, files in bad.items():
    print(f"  {n}  <- {', '.join(files)}")
sys.exit(1)
