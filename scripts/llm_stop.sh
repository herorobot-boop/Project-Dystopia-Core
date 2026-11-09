#!/usr/bin/env bash
set -uo pipefail
pkill -f "llama_cpp.server" 2>/dev/null || true
pkill -f "llama_cpp.server" 2>/dev/null || true
sleep 2
if curl -sf --max-time 2 http://127.0.0.1:8000/v1/models >/dev/null; then
  echo "❌ まだ生存"; exit 1
fi
echo "✅ LLM停止"
