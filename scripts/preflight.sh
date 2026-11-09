#!/usr/bin/env bash
fail=0
chk() { if eval "$2"; then echo "OK   $1"; else echo "NG   $1"; fail=1; fi; }
chk "aria2c"       "command -v aria2c >/dev/null"
chk "jq"           "command -v jq >/dev/null"
chk "curl"         "command -v curl >/dev/null"
chk "python3-venv" "python3 -c 'import venv' 2>/dev/null"
chk "VRAM 20GB+"   '[ "$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)" -ge 20000 ]'
chk "空き 110GB+"   '[ "$(df --output=avail -BG /workspace | tail -1 | tr -dc 0-9)" -ge 110 ]'
chk "set -euo 健在" "bash -n /workspace/Project-Dystopia-Core/genesis_ignition_omega.sh && ! grep -qx 'uo pipefail' /workspace/Project-Dystopia-Core/genesis_ignition_omega.sh"
chk "torch CUDA"      "python3 -c 'import torch,sys;sys.exit(0 if torch.cuda.is_available() else 1)' 2>/dev/null"
chk "comfy モジュール" "cd /workspace/ComfyUI && python3 -c 'import comfy' 2>/dev/null"
chk "ComfyUI 実体"     "[ -f /workspace/ComfyUI/main.py ]"
chk "Manager 実体"     "[ -f /workspace/ComfyUI/custom_nodes/ComfyUI-Manager/__init__.py ]"
chk fetch_missing 構文 python3 -c 'import ast;ast.parse(open("scripts/fetch_missing_assets.py").read())' 2>/dev/null
chk scan_nodes 構文  python3 -c 'import ast;ast.parse(open("scripts/scan_and_install_nodes.py").read())' 2>/dev/null
chk ノード6本 [ $(ls -d /workspace/ComfyUI/custom_nodes/*/ 2>/dev/null | wc -l) -ge 6 ]
chk Civitaiトークン [ -n "${CIVITAI_API_TOKEN:-}" ]
if [ "$fail" -ne 0 ]; then echo "--- 未解決あり ---"; exit 1; fi
echo "--- 通過 ---"
