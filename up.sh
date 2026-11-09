#!/usr/bin/env bash
# 1行でここまで来るための入口。済んだ工程は飛ばす。
set -uo pipefail
ROOT=/workspace/Project-Dystopia-Core
cd "$ROOT" 2>/dev/null || { echo "❌ $ROOT が無い"; exit 1; }

echo "=== 1/3 資材 ==="
bash scripts/provision.sh || exit 2

echo "=== 2/3 起動 ==="
bash scripts/boot_omega.sh || exit 3

echo
echo "✅ 準備完了。以下をコピペして使う"
echo
echo "  一覧        : bash run.sh ls"
echo "  静止画3枚   : bash run.sh still e2_menstoi_001 --n 3"
echo "  脱衣編集    : bash run.sh edit 0001 --lora"
echo "  部分編集    : bash run.sh edit 0001 \"Only pull the bra cup down\""
echo "  動画(下書)  : bash run.sh vid 0001 \"she slowly exhales\" --fast --frames 81"
echo "  動画(本番)  : bash run.sh vid 0001 \"she slowly exhales\""
echo "  採用        : bash run.sh pick 3 7"
echo "  不採用      : bash run.sh reject 4 9"
echo "  状態        : bash run.sh status"
echo
