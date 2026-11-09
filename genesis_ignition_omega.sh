#!/usr/bin/env bash
fetch_repo() {
  local repo="$1" dest="$2"
  if [ -d "${dest}" ] && [ -n "$(ls -A "${dest}" 2>/dev/null)" ]; then
    echo "[SKIP] ${dest}"; return 0
  fi
  local br
  br=$(curl -fsSL "https://api.github.com/repos/${repo}" | jq -r '.default_branch // empty')
  [ -z "${br}" ] && { echo "[FAIL] repo不明 ${repo}"; return 1; }
  mkdir -p "${dest}"
  curl -fsSL --max-time 300 "https://codeload.github.com/${repo}/tar.gz/refs/heads/${br}" -o /tmp/_r.tgz || return 1
  tar -xzf /tmp/_r.tgz -C "${dest}" --strip-components=1
  rm -f /tmp/_r.tgz
  echo "[OK] ${dest}"
}

set -e
install_c2patool_soft() {
    command -v c2patool >/dev/null 2>&1 && return 0
    local url
    url=$(curl -fsSL https://api.github.com/repos/contentauth/c2patool/releases/latest 2>/dev/null \
        | jq -r '.assets[]?.browser_download_url' 2>/dev/null \
        | grep -E 'x86_64-unknown-linux-gnu\.(tar\.gz|zip)$' | head -1)
    if [ -z "${url}" ]; then
        echo "WARN: c2patool の取得先を解決できない。C2PA 署名はスキップ"
        return 0
    fi
    local tmp; tmp=$(mktemp -d)
    if curl -fsSL "$url" -o "$tmp/pkg"; then
        case "$url" in
            *.zip) unzip -qo "$tmp/pkg" -d "$tmp" ;;
            *)     tar -xzf "$tmp/pkg" -C "$tmp" ;;
        esac
        find "$tmp" -type f -name c2patool -exec install -m755 {} /usr/local/bin/ \; 2>/dev/null
    fi
    rm -rf "$tmp"
    command -v c2patool >/dev/null 2>&1 \
        && echo "c2patool 導入済み" \
        || echo "WARN: c2patool 未導入。C2PA 署名はスキップ"
}
set -uo pipefail

echo "=========================================================="
echo "   Project Dystopia: Genesis Ignition Omega (v9.2)"
echo "=========================================================="

WORKSPACE=/workspace
CORE_DIR=${WORKSPACE}/Project-Dystopia-Core
COMFY_DIR=${WORKSPACE}/ComfyUI
GALLERY_DIR=${WORKSPACE}/smart-comfyui-gallery

# 1. 必須パッケージ
apt-get update || true
apt-get install -y -qq --no-install-recommends aria2 jq openssl python3-venv
install_c2patool_soft
command -v aria2c >/dev/null || { echo "[FATAL] aria2c 不在"; exit 1; }

# 2. コード同期
if [ ! -d "${CORE_DIR}/.git" ]; then
    fetch_repo herorobot-boop/Project-Dystopia-Core "${CORE_DIR}"
else
    cd "${CORE_DIR}" && git pull origin main
fi

# 2.5 ComfyUI 本体と Manager
if [ ! -d "${COMFY_DIR}/.git" ]; then
    fetch_repo comfyanonymous/ComfyUI "${COMFY_DIR}"
fi
pip install --no-cache-dir -r "${COMFY_DIR}/requirements.txt"
mkdir -p "${COMFY_DIR}/custom_nodes"
if [ ! -d "${COMFY_DIR}/custom_nodes/ComfyUI-Manager" ]; then
    fetch_repo ltdrdata/ComfyUI-Manager "${COMFY_DIR}/custom_nodes/ComfyUI-Manager"
fi
pip install --no-cache-dir -r "${COMFY_DIR}/custom_nodes/ComfyUI-Manager/requirements.txt" || true

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
    fetch_repo biagiomaf/smart-comfyui-gallery "${GALLERY_DIR}"
    cd "${GALLERY_DIR}" && pip install -r requirements.txt || true
fi

# 5. 兵站確保
python3 "${CORE_DIR}/scripts/fetch_missing_assets.py"

# 6. ノード解決
python3 "${CORE_DIR}/scripts/scan_and_install_nodes.py"

# 7. 出力ディレクトリと既定値（軍律16）
mkdir -p "${WORKSPACE}"/out/{raw,selected,rejected,video}
export DYSTOPIA_AUTO_VIDEO=${DYSTOPIA_AUTO_VIDEO:-0}

# 8. アロケータ最適化
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8
export CUDA_MODULE_LOADING=LAZY

# 9. GPU 判定（軍律14）
VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1)
if [ "${VRAM_MB}" -lt 28000 ]; then
    VRAM_FLAGS="--highvram --reserve-vram 2.0"
    export DYSTOPIA_WAN_TIER="5B"
    echo "[GPU] ${VRAM_MB}MB 検出 → Wan 5B モード"
else
    VRAM_FLAGS="--highvram --reserve-vram 2.0"
    export DYSTOPIA_WAN_TIER="14B"
    echo "[GPU] ${VRAM_MB}MB 検出 → Wan 14B 2段モード"
fi

# 10. ComfyUI 常駐
cd "${COMFY_DIR}"
python3 main.py --listen 0.0.0.0 --port 8188 ${VRAM_FLAGS} > "${WORKSPACE}/comfyui.log" 2>&1 &

for i in $(seq 1 60); do
    curl -s http://127.0.0.1:8188/system_stats > /dev/null && break
    sleep 2
    if [ "$i" -eq 60 ]; then
        echo "[FATAL] ComfyUI 起動失敗"
        tail -40 "${WORKSPACE}/comfyui.log"
        exit 1
    fi
done
echo "[ComfyUI] API 疎通確認完了"

# 11. 点火
cd "${CORE_DIR}"
exec python3 Main_Omega_Integrated.py
