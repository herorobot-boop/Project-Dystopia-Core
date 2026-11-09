#!/usr/bin/env bash
# 起動前検証 → ComfyUI確実起動 → スモークテスト。失敗時は理由を出して止まる。
set -uo pipefail

ROOT="${ROOT:-/workspace/Project-Dystopia-Core}"
COMFY="${COMFY:-/workspace/ComfyUI}"
PY="${PY:-/usr/local/bin/python3}"
LOG="${LOG:-/workspace/logs}"
RUNLOG="$LOG/comfy_$(date +%H%M%S).log"
PORT="${PORT:-8188}"

mkdir -p "$LOG"
cd "$ROOT" || exit 1

fail() { echo "❌ $*"; exit "${2:-1}"; }

# --- 1. Python ---
[ -x "$PY" ] || fail "python3 が無い: $PY"
"$PY" -c 'import torch; assert torch.cuda.is_available()' 2>/dev/null \
  || fail "torch CUDA 不可"

# --- 2. 必須モデル（サイズとマジックバイト） ---
need() {
  local p="$1" min="$2"
  [ -f "$p" ] || fail "欠落: $p"
  local s; s=$(stat -c%s "$p")
  [ "$s" -ge "$min" ] || fail "小さすぎ(${s}B): $p"
  head -c1 "$p" | grep -qE '^[<{]' && fail "HTML/JSON混入: $p"
  echo "  OK $(basename "$p") $((s/1000000))MB"
}

echo "--- モデル検証 ---"
need /workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf 7000000000
need "$COMFY/models/checkpoints/flux1-dev-fp8.safetensors" 15000000000
need "$COMFY/models/diffusion_models/qwen_image_edit_2509_fp8.safetensors" 15000000000
need "$COMFY/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors" 8000000000
need "$COMFY/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" 5000000000
need "$COMFY/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors" 7000000000
need "$COMFY/models/vae/wan2.2_vae.safetensors" 1000000000
need "$COMFY/models/vae/qwen_image_vae.safetensors" 200000000
need "$COMFY/models/loras/aidmaNSFWunlock-FLUX-V0.2.safetensors" 10000000

# --- 3. extra_model_paths.yaml ---
YML="$COMFY/extra_model_paths.yaml"
if ! "$PY" -c "import yaml,sys;yaml.safe_load(open('$YML'))" 2>/dev/null; then
  echo "  extra_model_paths.yaml を再生成"
  printf 'comfyui:\n  base_path: /workspace/models\n  llm: llm/\n  vlm: vlm/\n' > "$YML"
  "$PY" -c "import yaml;yaml.safe_load(open('$YML'))" || fail "YAML再生成に失敗"
fi

# --- 4. 既存プロセスとポート ---
alive() { curl -sf --max-time 3 "http://127.0.0.1:$PORT/system_stats" >/dev/null 2>&1; }

if alive; then
  echo "  既存ComfyUIを再利用"
else
  pkill -f "$COMFY/main.py" 2>/dev/null
  sleep 2
  echo "--- ComfyUI 起動 ---"
  ( cd "$COMFY" && nohup "$PY" main.py --listen 0.0.0.0 --port "$PORT" \
      --normalvram > "$RUNLOG" 2>&1 & )
  for i in $(seq 1 60); do
    sleep 2
    alive && break
    [ "$i" -eq 60 ] && { tail -n 25 "$RUNLOG"; fail "起動失敗。ログ: $RUNLOG" 3; }
  done
fi

curl -sf "http://127.0.0.1:$PORT/system_stats" | "$PY" -c \
  'import json,sys;d=json.load(sys.stdin);devs=d.get("devices",[]);print("  GPU:", devs[0]["name"] if devs else "None")' \
  || fail "system_stats が読めない" 3

# --- 5. VRAMパージ ---
curl -sf -X POST "http://127.0.0.1:$PORT/free" \
  -H 'Content-Type: application/json' \
  -d '{"unload_models":true,"free_memory":true}' >/dev/null
sleep 2

# --- 6. スモークテスト ---
echo "--- スモークテスト ---"
"$PY" "$ROOT/scripts/smoke_flux.py" || fail "スモーク失敗" 4

echo "✅ 起動完了"
