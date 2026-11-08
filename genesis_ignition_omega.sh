#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "   Project Dystopia: Genesis Ignition Omega (v9.0)"
echo "=========================================================="

WORKSPACE=/workspace
CORE_DIR=${WORKSPACE}/Project-Dystopia-Core
COMFY_DIR=${WORKSPACE}/ComfyUI
GALLERY_DIR=${WORKSPACE}/smart-comfyui-gallery

# 1. 必須パッケージ
apt-get update && apt-get install -y --no-install-recommends aria2 jq c2patool openssl python3-venv || true

# 2. コード同期
if [ ! -d "${CORE_DIR}/.git" ]; then
    git clone https://github.com/herorobot-boop/Project-Dystopia-Core.git "${CORE_DIR}"
else
    cd "${CORE_DIR}" && git pull origin main
fi

# 3. ComfyUI-Manager civitai.red 認証
MANAGER_CONFIG=${COMFY_DIR}/custom_nodes/ComfyUI-Manager/config.ini
if [ -f "${MANAGER_CONFIG}" ]; then
    sed -i 's|^base_domain = .*|base_domain = civitai.red|' "${MANAGER_CONFIG}"
    sed -i 's|^enable_nsfw = .*|enable_nsfw = True|' "${MANAGER_CONFIG}"
    if [ -n "${CIVITAI_API_TOKEN:-}" ]; then
        sed -i "s|^api_key = .*|api_key = ${CIVITAI_API_TOKEN}|" "${MANAGER_CONFIG}"
    fi
fi

# 4. DAM ビューアー
if [ ! -d "${GALLERY_DIR}" ]; then
    git clone https://github.com/biagiomaf/smart-comfyui-gallery.git "${GALLERY_DIR}"
    cd "${GALLERY_DIR}" && pip install -r requirements.txt || true
fi

# 5. 兵站確保
python3 "${CORE_DIR}/scripts/fetch_missing_assets.py"

# 6. ノード解決
python3 "${CORE_DIR}/scripts/scan_and_install_nodes.py"

# 7. アロケータ最適化
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8
export CUDA_MODULE_LOADING=LAZY

# 8. GPU 判定による VRAM モード分岐（軍律14）
VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1)
if [ "${VRAM_MB}" -lt 28000 ]; then
    VRAM_FLAGS="--lowvram --reserve-vram 2.0 --cpu-vae"
    export DYSTOPIA_WAN_TIER="5B"
    echo "[GPU] ${VRAM_MB}MB 検出 → Wan 5B モード"
else
    VRAM_FLAGS="--highvram --reserve-vram 2.0"
    export DYSTOPIA_WAN_TIER="14B"
    echo "[GPU] ${VRAM_MB}MB 検出 → Wan 14B 2段モード"
fi

# 9. ComfyUI 常駐起動
cd "${COMFY_DIR}"
python3 main.py --listen 0.0.0.0 --port 8188 ${VRAM_FLAGS} > "${WORKSPACE}/comfyui.log" 2>&1 &

until curl -s http://127.0.0.1:8188/system_stats > /dev/null; do
    sleep 2
done
echo "[ComfyUI] API 疎通確認完了"

# 10. 点火
cd "${CORE_DIR}"
exec python3 Main_Omega_Integrated.py
