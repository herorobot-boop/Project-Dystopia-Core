#!/usr/bin/env bash
set -uo pipefail
MAN=/workspace/Project-Dystopia-Core/scripts/manifest.tsv
bad=0
while IFS=$'\t' read -r url dest size sha; do
  [ -z "${url:-}" ] && continue
  [ "$size" = "*" ] && { echo "skip $(basename "$dest")"; continue; }
  out=$(curl -s -r 0-0 -D - -o /dev/null --max-time 25 "$url" \
        | tr -d '\r' | awk 'NR==1{print $2} /^content-range:/{print $3}')
  code=$(echo "$out" | sed -n 1p)
  total=$(echo "$out" | sed -n 2p | sed 's#.*/##')
  if [ "$code" != "200" ] && [ "$code" != "206" ]; then
    echo "❌ $code $(basename "$dest")"; bad=$((bad+1)); continue
  fi
  if [ -n "$total" ] && [ "$total" != "$size" ]; then
    echo "⚠ サイズ相違 $total != $size $(basename "$dest")"; bad=$((bad+1)); continue
  fi
  echo "OK $(basename "$dest")"
done < "$MAN"
[ "$bad" -eq 0 ] && echo "✅ 全URL有効" || { echo "❌ $bad 件異常"; exit 1; }
