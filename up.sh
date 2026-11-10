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
[ "$n" -ge 1 ] || { echo "❌ 0件"; exit 1; }
echo "  ${n} 件"
echo "=== 4/4 資材・起動 ==="
bash scripts/provision.sh || exit 2
bash scripts/boot_omega.sh || exit 3

cat <<'EOS'

✅ 準備完了。控えは docs/CHEATSHEET.md

  gen      : bash run.sh gen --place sentou --title "銭湯での中出し" "日本語の状況"
  ls       : bash run.sh ls
  still    : bash run.sh still <ID> --n 3
  compose  : bash run.sh compose 0001 out/ref/hand.png "his hand cups her breast"
  edit     : bash run.sh edit 0001 "Only pull the bra cup down"
  crowd    : bash run.sh crowd "five women changing, three men filming"
  vid下書  : bash run.sh vid 0001 "she slowly exhales" --fast --frames 81
  vid本番  : bash run.sh vid 0001 "she slowly exhales"
  motion   : bash run.sh motion 0001 "she slowly exhales"
  pick     : bash run.sh pick 3 7
EOS
