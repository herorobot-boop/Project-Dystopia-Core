#!/usr/bin/env bash
set -uo pipefail

COMFY=/workspace/ComfyUI
PY=/usr/local/bin/python3
ROOT=/workspace/Project-Dystopia-Core
RUNLOG="/workspace/logs/comfy_$(date +%H%M%S).log"
PORT=8188
PIN_DATE="2026-10-01"
mkdir -p /workspace/logs

fail() { echo "❌ $*"; exit "${2:-1}"; }

"$PY" -c 'import torch;assert torch.cuda.is_available()' 2>/dev/null || fail "CUDA不可"

FREE=$(df -BG --output=avail /workspace | tail -1 | tr -dc '0-9')
[ "${FREE:-0}" -ge 15 ] || fail "空き ${FREE}GB。15GB必要"

VRAM=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1 | tr -dc '0-9')
[ "${VRAM:-0}" -ge 20000 ] || fail "VRAM空き ${VRAM}MB。20GB必要（他プロセスを止める）"
echo "VRAM空き ${VRAM}MB"

YML="$COMFY/extra_model_paths.yaml"
if ! "$PY" -c "import yaml;yaml.safe_load(open('$YML'))" 2>/dev/null; then
  printf 'comfyui:\n  base_path: /workspace/models\n  llm: llm/\n' > "$YML"
fi

alive() { curl -sf --max-time 3 "http://127.0.0.1:$PORT/system_stats" >/dev/null 2>&1; }

start() {
  pkill -f "$COMFY/main.py" 2>/dev/null; sleep 2
  ( cd "$COMFY" && nohup "$PY" main.py --listen 0.0.0.0 --port "$PORT" \
      --normalvram > "$RUNLOG" 2>&1 & )
  for i in $(seq 1 60); do
    sleep 2; alive && return 0
    [ "$i" -eq 60 ] && return 1
  done
}

try_nodes() { "$PY" "$ROOT/scripts/preflight_nodes.py"; }

if alive; then echo "  既存を再利用"; else
  echo "--- 起動 ---"
  start || { tail -n 30 "$RUNLOG"; fail "起動失敗 $RUNLOG" 3; }
fi

curl -sf "http://127.0.0.1:$PORT/system_stats" | "$PY" -c \
  'import json,sys;d=json.load(sys.stdin);print("GPU:",d["devices"][0]["name"])' || fail "stats不可" 3

if try_nodes; then
  echo "  初回照合OK"
else
  echo "--- 段階2: ${PIN_DATE} に固定 ---"
  git -C "$COMFY" reset --hard -q 2>/dev/null
  git -C "$COMFY" fetch --unshallow -q 2>/dev/null || git -C "$COMFY" fetch --all -q 2>/dev/null
  ref=$(git -C "$COMFY" rev-list -1 --before="$PIN_DATE" origin/master 2>/dev/null \
        || git -C "$COMFY" rev-list -1 --before="$PIN_DATE" origin/main 2>/dev/null)
  if [ -n "$ref" ]; then
    git -C "$COMFY" checkout -q "$ref"
    start || fail "固定後の再起動失敗" 3
    if try_nodes; then echo "  固定で解消"; else
      echo "--- 段階3: 最新へ ---"
      git -C "$COMFY" checkout -q master 2>/dev/null || git -C "$COMFY" checkout -q main
      git -C "$COMFY" reset --hard -q origin/HEAD
      start || fail "最新化後の再起動失敗" 3
      try_nodes || fail "ノード不整合が解消しない。この行を貼り直す: bash /tmp/u" 5
    fi
  else
    fail "固定先が引けない。この行を貼り直す: bash /tmp/u" 5
  fi
fi

curl -sf -X POST "http://127.0.0.1:$PORT/free" -H 'Content-Type: application/json' \
  -d '{"unload_models":true,"free_memory":true}' >/dev/null; sleep 2

echo "--- スモーク ---"
"$PY" "$ROOT/scripts/smoke_flux.py" || fail "スモーク失敗" 4
echo "✅ 起動完了"
