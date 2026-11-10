#!/usr/bin/env bash
set -uo pipefail
cd /workspace/Project-Dystopia-Core || exit 1
PY=/usr/local/bin/python3
RAW=out/raw

case "${1:-}" in
  gen)
    shift; "$PY" scripts/llm_block.py "$@"
    ;;
  still)
    shift; f=$(find dist/blocks -name "$1.md" | head -1)
    [ -n "$f" ] || { echo "❌ ブロックが無い: $1"; exit 1; }
    shift; "$PY" scripts/gen_still.py "$f" "$@"
    ;;
  compose)
    shift; "$PY" scripts/compose_still.py "$@"
    ;;
  edit)
    shift; "$PY" scripts/edit_still.py "$@"
    ;;
  vid)
    shift; "$PY" scripts/wan5b_i2v.py "$@"
    ;;
  pick)
    shift; "$PY" scripts/promote.py "$@"
    ;;
  reject)
    shift; "$PY" scripts/promote.py --reject "$@"
    ;;
  ref)
    shift; mkdir -p out/ref; "$PY" scripts/gen_still.py "$@" --width 832 --height 1216
    ;;
  ls)
    echo "--- dist/blocks ---"
    find dist/blocks -name '*.md' 2>/dev/null | sed 's#dist/blocks/##' | sort | head -60
    echo "--- out/raw ---"
    ls -1 "$RAW" 2>/dev/null | grep -E '^[0-9]{4}\.' | sort || echo "(なし)"
    echo "--- out/ref ---"
    ls -1 out/ref 2>/dev/null || echo "(なし)"
    ;;
  status)
    "$PY" scripts/promote.py --list
    nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader 2>/dev/null \
      || "$PY" -c 'import torch;f,t=torch.cuda.mem_get_info();print("free",f//1048576,"MB")'
    ;;
  *)
    echo "使い方: bash run.sh {gen|still|compose|edit|vid|pick|reject|ref|ls|status}"
    ;;
esac
