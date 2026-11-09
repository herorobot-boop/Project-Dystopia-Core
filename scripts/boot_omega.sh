#!/usr/bin/env bash
set -uo pipefail

COMFY=/workspace/ComfyUI
PY=/usr/local/bin/python3
ROOT=/workspace/Project-Dystopia-Core
LOG=/workspace/logs
RUNLOG="$LOG/comfy_$(date +%H%M%S).log"
PORT=8188
mkdir -p "$LOG"

fail() { echo "❌ $*"; exit "${2:-1}"; }

"$PY" -c 'import torch;assert torch.cuda.is_available()' 2>/dev/null || fail "CUDA不可"
free -g | awk 'NR==2{exit ($7<20)}' || fail "空きメモリ不足"

YML="$COMFY/extra_model_paths.yaml"
if ! "$PY" -c "import yaml;yaml.safe_load(open('$YML'))" 2>/dev/null; then
  printf 'comfyui:\n  base_path: /workspace/models\n  llm: llm/\n' > "$YML"
fi

alive() { curl -sf --max-time 3 "http://127.0.0.1:$PORT/system_stats" >/dev/null 2>&1; }

if alive; then
  echo "  既存を再利用"
else
  pkill -f "$COMFY/main.py" 2>/dev/null; sleep 2
  ( cd "$COMFY" && nohup "$PY" main.py --listen 0.0.0.0 --port "$PORT" \
      --normalvram > "$RUNLOG" 2>&1 & )
  for i in $(seq 1 60); do
    sleep 2; alive && break
    [ "$i" -eq 60 ] && { tail -n 30 "$RUNLOG"; fail "起動失敗 $RUNLOG" 3; }
  done
fi

curl -sf "http://127.0.0.1:$PORT/system_stats" | "$PY" -c \
  'import json,sys;d=json.load(sys.stdin);print("GPU:",d["devices"][0]["name"])' || fail "stats不可" 3

curl -sf -X POST "http://127.0.0.1:$PORT/free" -H 'Content-Type: application/json' \
  -d '{"unload_models":true,"free_memory":true}' >/dev/null; sleep 2

echo "--- スモーク ---"
"$PY" "$ROOT/scripts/smoke_flux.py" || fail "スモーク失敗" 4
echo "✅ 起動完了"
