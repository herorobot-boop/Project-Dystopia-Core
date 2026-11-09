#!/usr/bin/env bash
set -uo pipefail

COMFY=/workspace/ComfyUI
PY=/usr/local/bin/python3
ROOT=/workspace/Project-Dystopia-Core
RUNLOG="/workspace/logs/comfy_$(date +%H%M%S).log"
PORT=8188
mkdir -p /workspace/logs

fail() { echo "❌ $*"; exit "${2:-1}"; }

"$PY" -c 'import torch;assert torch.cuda.is_available()' 2>/dev/null || fail "CUDA不可"
FREE=$(df -BG --output=avail /workspace | tail -1 | tr -dc '0-9')
[ "${FREE:-0}" -ge 15 ] || fail "空き ${FREE}GB。15GB必要"

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

if alive; then echo "  既存を再利用"; else
  echo "--- 起動 ---"
  start || { tail -n 30 "$RUNLOG"; fail "起動失敗 $RUNLOG" 3; }
fi

curl -sf "http://127.0.0.1:$PORT/system_stats" | "$PY" -c \
  'import json,sys;d=json.load(sys.stdin);print("GPU:",d["devices"][0]["name"])' || fail "stats不可" 3

echo "--- ノード照合 ---"
if ! "$PY" "$ROOT/scripts/preflight_nodes.py"; then
  echo "--- ComfyUI 更新を試行 ---"
  git -C "$COMFY" pull --ff-only >/dev/null 2>&1
  start || fail "再起動失敗" 3
  "$PY" "$ROOT/scripts/preflight_nodes.py" || fail "ノード不整合が解消しない" 5
fi

curl -sf -X POST "http://127.0.0.1:$PORT/free" -H 'Content-Type: application/json' \
  -d '{"unload_models":true,"free_memory":true}' >/dev/null; sleep 2

echo "--- スモーク ---"
"$PY" "$ROOT/scripts/smoke_flux.py" || fail "スモーク失敗" 4
echo "✅ 起動完了"
