#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "   🐺 Project Dystopia: Genesis Ignition Omega (v8.2)     "
echo "=========================================================="

WORKSPACE="/workspace"
CORE_DIR="${WORKSPACE}/Project-Dystopia-Core"
COMFY_DIR="${WORKSPACE}/ComfyUI"

# 1. 必須パッケージの検証と導入
apt-get update && apt-get install -y --no-install-recommends aria2 jq c2patool openssl || true

# 2. 環境変数の検証
if [ -z "${CIVITAI_API_TOKEN:-}" ]; then
    echo "⚠️ [WARN] CIVITAI_API_TOKEN が未設定です。Civitai.red の認証ダウンロードが失敗する可能性があります。"
fi

# 3. GitHubプライベートリポジトリの同期
if [ -n "${GITHUB_TOKEN:-}" ]; then
    git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
fi

if [ ! -d "${CORE_DIR}/.git" ]; then
    echo "📥 [Git] リポジトリをクローン中..."
    git clone "https://github.com/herorobot-boop/Project-Dystopia-Core.git" "${CORE_DIR}"
else
    echo "🔄 [Git] 最新コードを同期中..."
    cd "${CORE_DIR}" && git pull origin main
fi

# 4. ComfyUI-Manager の civitai.red ドメイン強制適用
MANAGER_CONFIG="${COMFY_DIR}/custom_nodes/ComfyUI-Manager/config.ini"
if [ -f "${MANAGER_CONFIG}" ]; then
    echo "🔧 [Config] ComfyUI-Manager を civitai.red 認証モードへ構成..."
    sed -i "s/^base_domain = .*/base_domain = civitai.red/" "${MANAGER_CONFIG}"
    sed -i "s/^enable_nsfw = .*/enable_nsfw = True/" "${MANAGER_CONFIG}"
    if [ -n "${CIVITAI_API_TOKEN:-}" ]; then
        sed -i "s/^api_key = .*/api_key = ${CIVITAI_API_TOKEN}/" "${MANAGER_CONFIG}"
    fi
fi

# 5. 実弾モデルの一括直接着弾（兵站確保：所要10-15分）
python3 "${CORE_DIR}/scripts/fetch_missing_assets.py"

# 6. 未導入カスタムノードの自動解決
python3 "${CORE_DIR}/scripts/scan_and_install_nodes.py"

# 7. PyTorch アロケータ最適化（VRAM断片化防止）
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,garbage_collection_threshold:0.8"
export CUDA_MODULE_LOADING="LAZY"

# 8. ComfyUI デーモンのバックグラウンド起動
echo "🖥️ [ComfyUI] サーバーを常駐起動中..."
cd "${COMFY_DIR}"
python3 main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --highvram \
    --reserve-vram 2.0 \
    --cpu-vae > "${WORKSPACE}/comfyui.log" 2>&1 &

# ComfyUI API の起動完了を待機
echo "⏳ [ComfyUI] API 応答待機中 (ポート 8188)..."
until curl -s http://127.0.0.1:8188/system_stats > /dev/null; do
    sleep 2
done
echo "✅ [ComfyUI] API 疎通確認完了。"

# 9. メインオーケストレーター点火
echo "🔥 [Ignition] Main_Omega_Integrated.py 起動！"
cd "${CORE_DIR}"
exec python3 Main_Omega_Integrated.py
