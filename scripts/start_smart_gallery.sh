#!/usr/bin/env bash
set -uo pipefail
ROOT=/workspace/Project-Dystopia-Core
GALLERY_DIR=/workspace/smart-comfyui-gallery
PORT=8080
LOG=/workspace/logs/gallery.log
mkdir -p /workspace/logs "$ROOT/out/raw"

if [ ! -d "$GALLERY_DIR" ]; then
  echo "取得中..."
  curl -fsSL "https://codeload.github.com/iamthebestguy/smart-comfyui-gallery/tar.gz/refs/heads/main" \
    -o /tmp/g.tgz && mkdir -p "$GALLERY_DIR" && tar -xzf /tmp/g.tgz -C "$GALLERY_DIR" --strip-components=1 \
    || { echo "❌ 取得失敗"; exit 1; }
fi

if curl -sf --max-time 2 "http://127.0.0.1:${PORT}/" >/dev/null; then
  echo "既に起動中: http://127.0.0.1:${PORT}/"; exit 0
fi

cd "$GALLERY_DIR" || exit 1
nohup /usr/local/bin/python3 server.py --host 0.0.0.0 --port "$PORT" \
  --output-dir "$ROOT/out/raw" >> "$LOG" 2>&1 &
for _ in $(seq 1 20); do
  sleep 1
  curl -sf --max-time 2 "http://127.0.0.1:${PORT}/" >/dev/null && { echo "✅ Port ${PORT}"; exit 0; }
done
tail -n 20 "$LOG"; echo "❌ 起動失敗"; exit 1
