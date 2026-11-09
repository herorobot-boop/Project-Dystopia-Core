#!/usr/bin/env bash
set -uo pipefail
cd /workspace/Project-Dystopia-Core || exit 1
PY=/usr/local/bin/python3
RAW=out/raw

case "${1:-}" in
  ls)
    echo "--- dist/blocks ---"
    find dist/blocks -name '*.md' 2>/dev/null | sed 's#dist/blocks/##' | sort | head -60
    echo "--- out/raw ---"
    ls -1 "$RAW" 2>/dev/null | grep -E '^[0-9]{4}\.' | sort || echo "(なし)"
    ;;
  still)
    shift; f=$(find dist/blocks -name "$1.md" | head -1)
    [ -n "$f" ] || { echo "❌ ブロックが無い: $1"; exit 1; }
    shift; "$PY" scripts/gen_still.py "$f" "$@"
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
  status)
    "$PY" scripts/promote.py --list
    nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
    ;;
  *)
    echo "使い方: bash run.sh {ls|still|edit|vid|pick|reject|status}"
    ;;
esac
