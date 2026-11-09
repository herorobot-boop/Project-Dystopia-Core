cat > scripts/start_smart_gallery.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

GALLERY_DIR="/workspace/smart-comfyui-gallery"
LOG_FILE="/workspace/gallery.log"

if [ ! -d "${GALLERY_DIR}" ]; then
  echo "❌ ${GALLERY_DIR} がありません。git clone してください。"
  exit 1
fi

cd "${GALLERY_DIR}"
export OUTPUT_DIR="/workspace/ComfyUI/output"
export PORT=8000

echo "📱 [DAM] smart-comfyui-gallery を Port 8000 で起動中..."
nohup python3 server.py --host 0.0.0.0 --port 8000 --output-dir "${OUTPUT_DIR}" >> "${LOG_FILE}" 2>&1 &
echo "✅ [DAM Ready] スマホブラウザから Port 8000 へアクセス可能です。"
echo "   ログ: ${LOG_FILE}"
SH
chmod +x scripts/start_smart_gallery.sh
