#!/usr/bin/env bash
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive

MAN=/workspace/Project-Dystopia-Core/scripts/manifest.tsv
COMFY=/workspace/ComfyUI
PY=/usr/local/bin/python3
mkdir -p /workspace/models/llm /workspace/logs /workspace/Project-Dystopia-Core/out/raw

fail() { echo "❌ $*"; exit "${2:-1}"; }
command -v git >/dev/null || fail "git が無い。git入りテンプレートを選ぶこと"

need=0
while IFS=$'\t' read -r url dest size sha; do
  [ -z "${url:-}" ] && continue
  [ "$size" = "*" ] && continue
  if [ -f "$dest" ] && [ "$(stat -c%s "$dest")" = "$size" ]; then continue; fi
  need=$((need + size))
done < "$MAN"
need_gb=$(( need / 1073741824 + 15 ))

FREE=$(df -BG --output=avail /workspace | tail -1 | tr -dc '0-9')
[ -n "$FREE" ] || fail "空き容量を判定できない"
if [ "$need" -gt 0 ] && [ "$FREE" -lt "$need_gb" ]; then
  fail "不足分 ${need_gb}GB に対し空き ${FREE}GB。200GBにすること"
fi
echo "不足分 $(( need / 1073741824 ))GB / 空き ${FREE}GB"

[ -d "$COMFY" ] || fail "ComfyUI が無い。テンプレートは PyTorch ではなく ComfyUI"

command -v aria2c >/dev/null || { apt-get update -qq && apt-get install -y -qq aria2 >/dev/null; }
command -v ffmpeg  >/dev/null || apt-get install -y -qq ffmpeg >/dev/null
command -v aria2c >/dev/null || fail "aria2c 導入失敗"

PIPOPT=""
"$PY" -m pip install -q pyyaml 2>/dev/null || {
  PIPOPT="--break-system-packages"
  "$PY" -m pip install -q $PIPOPT pyyaml || fail "pyyaml 導入失敗"
}

if [ ! -d "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" ]; then
  for i in 1 2 3; do
    git clone --depth 1 https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite \
      "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" && break
    sleep 5
  done
fi
[ -d "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite" ] || fail "VHS 取得失敗"
"$PY" -m pip install -q $PIPOPT -r \
  "$COMFY/custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt" 2>/dev/null

bash /workspace/Project-Dystopia-Core/scripts/verify_urls.sh || fail "URL検証で停止" 2

if [ -n "${HF_TOKEN:-}" ]; then
  AUTH=(--header="Authorization: Bearer ${HF_TOKEN}")
else
  AUTH=()
fi

while IFS=$'\t' read -r url dest size sha; do
  [ -z "${url:-}" ] && continue
  mkdir -p "$(dirname "$dest")"
  if [ "$size" != "*" ] && [ -f "$dest" ] && [ "$(stat -c%s "$dest")" = "$size" ]; then
    echo "  skip $(basename "$dest")"; continue
  fi
  aria2c -c -x4 -s4 -k1M --file-allocation=none --max-tries=8 --retry-wait=10 \
    --console-log-level=warn --summary-interval=0 ${AUTH[@]+"${AUTH[@]}"} \
    -d "$(dirname "$dest")" -o "$(basename "$dest")" "$url" \
    || fail "DL失敗 $(basename "$dest")"
done < "$MAN"

while IFS=$'\t' read -r url dest size sha; do
  [ -z "${url:-}" ] && continue
  [ -f "$dest" ] || fail "欠落 $(basename "$dest")"
  s=$(stat -c%s "$dest")
  [ "$s" -ge 1048576 ] || fail "小さすぎ $(basename "$dest")"
  head -c1 "$dest" | grep -qE '^[<{]' && fail "HTML混入 $(basename "$dest")"
  if [ "$size" != "*" ]; then
    [ "$s" = "$size" ] || fail "サイズ不一致 $(basename "$dest")"
    [ "$(sha256sum "$dest" | cut -d' ' -f1)" = "$sha" ] || fail "SHA不一致 $(basename "$dest")"
  fi
  echo "  OK $(basename "$dest")"
done < "$MAN"

echo "✅ 資材完了"
