#!/usr/bin/env bash
set -uo pipefail
ROOT=/workspace/Project-Dystopia-Core
cd "$ROOT" 2>/dev/null || { echo "❌ $ROOT が無い"; exit 1; }
PY=/usr/local/bin/python3
mkdir -p out/raw out/ref

echo "=== 1/4 台帳 → YAML ==="
"$PY" scripts/import_tsv.py || exit 1

echo "=== 2/4 検品 ==="
"$PY" scripts/validate.py || { echo "❌ 検品NG"; exit 1; }

echo "=== 3/4 ブロック生成 ==="
"$PY" scripts/build.py || exit 1
n=$(find dist/blocks -name '*.md' 2>/dev/null | wc -l)
[ "$n" -ge 1 ] || { echo "❌ ブロックが0件"; exit 1; }
echo "  ブロック ${n} 件"

echo "=== 4/4 資材・起動 ==="
bash scripts/provision.sh || exit 2
bash scripts/boot_omega.sh || exit 3

echo
echo "✅ 準備完了"
echo
echo "  生成     : bash run.sh gen --place lingerie_shop --title \"試着の手伝い\" \"日本語で状況\""
echo "  一覧     : bash run.sh ls"
echo "  静止画3枚: bash run.sh still <id> --n 3"
echo "  2人合成  : bash run.sh compose 0001 out/ref/hand.png \"his hand cups her breast\""
echo "  脱衣編集 : bash run.sh edit 0001 --lora"
echo "  動画下書 : bash run.sh vid 0001 \"she slowly exhales\" --fast --frames 81"
echo "  動画本番 : bash run.sh vid 0001 \"she slowly exhales\""
echo "  採用     : bash run.sh pick 3 7"
