#!/usr/bin/env bash
set -uo pipefail
ROOT=/workspace/Project-Dystopia-Core
PORT=8080
LOG=/workspace/logs/gallery.log
mkdir -p /workspace/logs "$ROOT/out/raw"

if curl -sf --max-time 2 "http://127.0.0.1:${PORT}/" >/dev/null; then
  echo "既に起動中: Port ${PORT}"; exit 0
fi

nohup /usr/local/bin/python3 "$ROOT/scripts/gallery_server.py" "$PORT" >> "$LOG" 2>&1 &
for _ in $(seq 1 15); do
  sleep 1
  curl -sf --max-time 2 "http://127.0.0.1:${PORT}/" >/dev/null && { echo "✅ Port ${PORT}"; exit 0; }
done
tail -n 20 "$LOG"; echo "❌ 起動失敗"; exit 1
