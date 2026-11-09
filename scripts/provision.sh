#!/usr/bin/env bash
set -uo pipefail

MAN=/workspace/Project-Dystopia-Core/scripts/manifest.tsv
COMFY=/workspace/ComfyUI
PY=/usr/local/bin/python3
LOG=/workspace/logs
mkdir -p "$LOG" /workspace/models/llm

fail() { echo "❌ $*"; exit "${2:-1}"; }

command -v aria2c >/dev/null || { apt-get update -qq && apt-get install -y -qq aria2 >/dev/null; }
command -v ffmpeg  >/dev/null || { apt-get install -y -qq ffmpeg >/dev/null; }
command -v aria2c >/dev/null || fail "aria2c 導入失敗"
command -v ffmpeg  >/dev/null || fail "ffmpeg 導入失敗"

[ -d "$COMFY" ] || fail "ComfyUI が無い。ComfyUIテンプレートでPodを立てること"

echo "--- ノード ---"
if [ ! -d "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" ]; then
  for i in 1 2 3; do
    git clone --depth 1 https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite \
      "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" && break
    echo "  再試行 $i"; sleep 5
  done
fi
[ -d "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" ] || fail "VHS 取得失敗"
"$PY" -m pip install -q -r "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt" 2>/dev/null

echo "--- URL検証 ---"
bash /workspace/Project-Dystopia-Core/scripts/verify_urls.sh || fail "URL検証で停止" 2

echo "--- ダウンロード ---"
while IFS=$'\t' read -r url dest size sha; do
  [ -z "${url:-}" ] && continue
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ]; then
    cur=$(stat -c%s "$dest")
    if [ "$cur" = "$size" ]; then echo "  skip $(basename "$dest")"; continue; fi
    echo "  再開 $(basename "$dest") ${cur}/${size}"
  fi
  aria2c -c -x8 -s8 -k1M --file-allocation=none --max-tries=5 \
    --retry-wait=5 --console-log-level=warn --summary-interval=0 \
    -d "$(dirname "$dest")" -o "$(basename "$dest")" "$url" \
    || fail "DL失敗 $(basename "$dest")"
done < "$MAN"

echo "--- 検証 ---"
while IFS=$'\t' read -r url dest size sha; do
  [ -z "${url:-}" ] && continue
  [ -f "$dest" ] || fail "欠落 $(basename "$dest")"
  s=$(stat -c%s "$dest")
  [ "$s" = "$size" ] || fail "サイズ不一致 $(basename "$dest") $s != $size"
  head -c1 "$dest" | grep -qE '^[<{]' && fail "HTML混入 $(basename "$dest")"
  a=$(sha256sum "$dest" | cut -d' ' -f1)
  [ "$a" = "$sha" ] || fail "SHA不一致 $(basename "$dest")"
  echo "  OK $(basename "$dest")"
done < "$MAN"

echo "✅ 資材完了"
