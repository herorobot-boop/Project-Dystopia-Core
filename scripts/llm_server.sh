#!/usr/bin/env bash
set -uo pipefail
PY=/usr/local/bin/python3
MODEL=/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf
LOG=/workspace/logs/llm.log
mkdir -p /workspace/logs

if curl -sf --max-time 2 http://127.0.0.1:8000/v1/models >/dev/null; then
  echo "  既存LLMを再利用"; exit 0
fi

"$PY" -c "import llama_cpp" 2>/dev/null || {
  for url in \
    https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.16/llama_cpp_python-0.3.16-cp311-cp311-linux_x86_64.whl \
    https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.16/llama_cpp_python-0.3.16-cp311-cp311-manylinux_2_35_x86_64.whl ; do
    "$PY" -m pip install -q "$url" 2>/dev/null && break
  done
  "$PY" -c "import llama_cpp" 2>/dev/null || {
    echo "  wheel失敗。ソースからビルド（10分程度）"
    CMAKE_ARGS="-DGGML_CUDA=on" "$PY" -m pip install -q llama-cpp-python
  }
}

"$PY" -c "import llama_cpp" 2>/dev/null || { echo "❌ llama_cpp 導入失敗"; exit 1; }

nohup "$PY" -m llama_cpp.server --model "$MODEL" --n_ctx 8192 --n_gpu_layers -1 \
  --host 127.0.0.1 --port 8000 --chat_format chatml > "$LOG" 2>&1 &

for i in $(seq 1 60); do
  sleep 2
  curl -sf --max-time 2 http://127.0.0.1:8000/v1/models >/dev/null && { echo "✅ LLM起動"; exit 0; }
done
tail -n 20 "$LOG"; echo "❌ LLM起動失敗"; exit 1
