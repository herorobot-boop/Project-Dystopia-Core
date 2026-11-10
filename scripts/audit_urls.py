#!/usr/bin/env python3
import re, subprocess, sys
from pathlib import Path

pat = re.compile(r'https://[^\s"\')]+')
bad = []
for p in sorted(Path("scripts").glob("*.py")):
    for u in set(pat.findall(p.read_text(errors="ignore"))):
        if "127.0.0.1" in u or "github.com/herorobot" in u:
            continue
        code = subprocess.run(
            ["curl", "-sIL", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", u],
            capture_output=True, text=True).stdout.strip()[-3:]
        if code not in ("200", "302"):
            bad.append((code, u))
if not bad:
    print("[OK] URLは全て生存"); sys.exit(0)
print("[NG] 死んでいるURL:")
for c, u in bad: print(f"  {c}  {u}")
sys.exit(1)
