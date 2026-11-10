#!/usr/bin/env bash
set -uo pipefail
ROOT=/workspace/Project-Dystopia-Core
cd "$ROOT" 2>/dev/null || { echo "❌ $ROOT が無い"; exit 1; }
PY=/usr/local/bin/python3
mkdir -p out/raw out/ref

echo "=== 1/5 台帳 → YAML ==="
"$PY" scripts/import_tsv.py || exit 1
echo "=== 2/5 検品 ==="
"$PY" scripts/validate.py || { echo "❌ 検品NG"; exit 1; }
echo "=== 3/5 ブロック生成 ==="
"$PY" scripts/build.py || exit 1
n=$(find dist/blocks -name '*.md' 2>/dev/null | wc -l)
[ "$n" -ge 1 ] || { echo "❌ 0件"; exit 1; }
echo "  ${n} 件"
echo "=== 4/5 資材・起動 ==="
bash scripts/provision.sh || exit 2
bash scripts/boot_omega.sh || exit 3
echo "=== 5/5 監査 ==="
bash scripts/audit_all.sh || echo "⚠ 監査NG。上の一覧を確認"

echo "▶ bash menu.sh   ← これを打てばメニューが出ます"
