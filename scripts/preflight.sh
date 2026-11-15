#!/usr/bin/env bash
set -uo pipefail
fail=0
PY=/usr/local/bin/python3
chk() { if ( eval "$2" ); then echo "OK   $1"; else echo "NG   $1"; fail=1; fi; }
chk "aria2c"       "command -v aria2c >/dev/null"
chk "jq"           "command -v jq >/dev/null"
chk "curl"         "command -v curl >/dev/null"
chk "python3-venv" "$PY -c 'import venv' 2>/dev/null"
chk "VRAM 20GB+"   '[ "$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)" -ge 20000 ]'
chk "空き 95GB+"    '[ "$(df --output=avail -BG /workspace | tail -1 | tr -dc 0-9)" -ge 95 ]'
chk "set -euo 健在" "bash -n /workspace/Project-Dystopia-Core/genesis_ignition_omega.sh && ! grep -qx 'uo pipefail' /workspace/Project-Dystopia-Core/genesis_ignition_omega.sh"
chk "torch CUDA"      "$PY -c 'import torch,sys;sys.exit(0 if torch.cuda.is_available() else 1)' 2>/dev/null"
chk "comfy モジュール" "cd /workspace/ComfyUI && $PY -c 'import comfy' 2>/dev/null"
chk "ComfyUI 実体"     "[ -f /workspace/ComfyUI/main.py ]"
chk "Manager 実体"     "[ -f /workspace/ComfyUI/custom_nodes/ComfyUI-Manager/__init__.py ]"
chk "fetch_missing 構文" "$PY -m py_compile /workspace/Project-Dystopia-Core/scripts/fetch_missing_assets.py"
chk "scan_nodes 構文" "$PY -m py_compile /workspace/Project-Dystopia-Core/scripts/scan_and_install_nodes.py"
chk "ノード6本" "[ \$(ls -d /workspace/ComfyUI/custom_nodes/*/ 2>/dev/null | wc -l) -ge 6 ]"
chk "Civitaiトークン" '[ -n "${CIVITAI_API_TOKEN:-}${CIVITAI_TOKEN:-}" ]'
if [ "$fail" -ne 0 ]; then echo "--- 未解決あり ---"; exit 1; fi
echo "--- 通過 ---"
