#!/usr/bin/env python3
import re, sys
from pathlib import Path

ROOT = Path("/workspace/ComfyUI/models")
pat = re.compile(r'["\']([A-Za-z0-9_.\-]+\.(?:safetensors|gguf|pt|pth|bin))["\']')
bad = set()
for p in sorted(Path("scripts").glob("*.py")):
    for name in pat.findall(p.read_text(errors="ignore")):
        if not any(ROOT.rglob(name)):
            bad.add(name)
if not bad:
    print("[OK] 参照モデルは全て実在"); sys.exit(0)
print("[NG] 実在しない参照:")
for n in sorted(bad): print("  ", n)
sys.exit(1)
