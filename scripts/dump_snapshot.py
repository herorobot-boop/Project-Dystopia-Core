#!/usr/bin/env python3
"""監査用スナップショット。指定パスのコードを行番号付きで1枚に連結する。"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = [
    "scripts/comfy_api_bridge.py", "scripts/audit_gate.py", "scripts/edit_still.py",
    "scripts/compose_still.py", "scripts/Main_Omega_Integrated.py",
    "scripts/preflight_nodes.py", "scripts/fetch_missing_assets.py",
    "scripts/mutation_lab.py", "scripts/import_tsv.py", "scripts/genesis_ignition_omega.sh",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*", default=DEFAULT)
    ap.add_argument("--out", default="SNAPSHOT.txt")
    args = ap.parse_args()

    chunks = []
    for rel in args.paths:
        p = ROOT / rel
        if not p.exists():
            chunks.append(f"===== {rel} =====\n(存在しない)\n")
            continue
        body = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        numbered = "\n".join(f"{i:4d}| {l}" for i, l in enumerate(body, 1))
        chunks.append(f"===== {rel} ({len(body)}行) =====\n{numbered}\n")

    (ROOT / args.out).write_text("\n".join(chunks), encoding="utf-8")
    print(f"{len(chunks)}ファイル → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
