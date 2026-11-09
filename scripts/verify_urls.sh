#!/usr/bin/env bash
set -uo pipefail
MAN=/workspace/Project-Dystopia-Core/scripts/manifest.tsv
bad=0
while IFS=$'\t' read -r url dest size sha; do
  [ -z "${url:-}" ] && continue
  code=$(curl -sIL -o /dev/null -w '%{http_code}' --max-time 20 "$url")
  clen=$(curl -sIL --max-time 20 "$url" | tr -d '\r' | awk 'tolower($1)=="content-length:"{v=$2} END{print v}')
  if [ "$code" != "200" ]; then echo "❌ $code $url"; bad=$((bad+1)); continue; fi
  if [ -n "$clen" ] && [ "$clen" != "$size" ]; then
    echo "⚠ サイズ相違 $clen != $size $url"; bad=$((bad+1)); continue
  fi
  echo "OK $code $(basename "$dest")"
done < "$MAN"
[ "$bad" -eq 0 ] && echo "✅ 全URL有効" || { echo "❌ $bad 件異常"; exit 1; }
