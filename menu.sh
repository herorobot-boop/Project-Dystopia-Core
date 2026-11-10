#!/usr/bin/env bash
set -uo pipefail
cd /workspace/Project-Dystopia-Core || exit 1
PY=/usr/local/bin/python3
RAW=out/raw
LLM_PY=$(find /workspace -name python3 -path '*/.venv-cu128/*' 2>/dev/null | head -n1)
[ -n "${LLM_PY:-}" ] || LLM_PY=$PY

PLACES="lingerie_shop:ランジェリーショップ
open_locker:仕切りなし更衣室
sokutei:採寸会
sentou:銭湯
menstoi:男子トイレ
massage:マッサージ店
gym:ジム
byouin:触診・検診
shampoo:美容室の洗髪台
elevator:エレベーター
library:図書館
netcafe:ネットカフェ
starbucks:カフェ
petshop:ペットショップ
bukatsu:部活の部室"

hr() { printf '─%.0s' {1..60}; echo; }
pause() { read -rp "Enterで戻る " _; }

pick_place() {
  echo "場所を選んでください"
  local i=1
  while IFS=: read -r id name; do
    printf '  %2d) %s\n' "$i" "$name"
    eval "P_$i=$id"; i=$((i+1))
  done <<< "$PLACES"
  echo "  m) 自分で英単語を入力"
  read -rp "番号: " n
  if [ "$n" = "m" ]; then read -rp "英小文字で入力: " id; echo "$id"; return; fi
  eval "echo \$P_$n"
}

pick_block() {
  local list=() f
  while read -r f; do list+=("$f"); done < <(find dist/blocks -name '*.md' 2>/dev/null | sort)
  [ ${#list[@]} -gt 0 ] || { echo ""; return; }
  local i=1
  for f in "${list[@]}"; do
    printf '  %2d) %s\n' "$i" "$(basename "$f" .md)"
    eval "B_$i=$f"; i=$((i+1))
  done
  read -rp "番号: " n
  eval "echo \$B_$n"
}

pick_raw() {
  local list=() f
  while read -r f; do list+=("$f"); done < <(ls -1 $RAW 2>/dev/null | grep -E '^[0-9]{4}\.' | sort)
  [ ${#list[@]} -gt 0 ] || { echo ""; return; }
  local i=1
  for f in "${list[@]}"; do printf '  %2d) %s\n' "$i" "$f"; eval "R_$i=$f"; i=$((i+1)); done
  read -rp "番号: " n
  eval "echo \$R_$n"
}

while true; do
  hr
  echo " Project Dystopia メニュー"
  hr
  echo "  1) 新しいシチュエーションを登録（日本語で書く）"
  echo "  2) 静止画を出す"
  echo "  3) 一部だけ変える（局部だけズラす）"
  echo "  4) 2〜3人を合成する"
  echo "  5) 動画にする（下書き）"
  echo "  6) 動画にする（本番・動き重視）"
  echo "  7) 一覧を見る"
  echo "  8) 採用 / 不採用"
  echo "  9) 状態（GPU・件数）"
  echo "  0) 終了"
  read -rp "番号: " c
  case $c in
    1)
      echo; pid=$(pick_place)
      [ -n "$pid" ] || continue
      read -rp "短い名前（日本語）: " title
      read -rp "状況を自由に日本語で: " sit
      echo; echo "生成中..."
      "$LLM_PY" scripts/llm_block.py --place "$pid" --title "$title" "$sit"
      pause ;;
    2)
      echo; echo "ブロック:"; b=$(pick_block)
      [ -n "$b" ] || { echo "ブロックがありません。先に1)"; pause; continue; }
      read -rp "枚数 [3]: " n; n=${n:-3}
      read -rp "脱がせる? [y/N]: " nd
      args=(--n "$n"); [ "$nd" = "y" ] && args+=(--nude)
      "$PY" scripts/gen_still.py "$b" "${args[@]}"
      pause ;;
    3)
      echo; echo "対象:"; r=$(pick_raw)
      [ -n "$r" ] || { echo "画像がありません"; pause; continue; }
      read -rp "何をする?（例: Only pull the bra cup down）: " ins
      echo "  1) 部分だけ  2) 全部脱がせる"
      read -rp "番号: " m
      if [ "$m" = "2" ]; then "$PY" scripts/edit_still.py "$r" "$ins" --lora
      else "$PY" scripts/edit_still.py "$r" "$ins"; fi
      pause ;;
    4)
      echo; echo "土台:"; r=$(pick_raw)
      [ -n "$r" ] || { echo "画像がありません"; pause; continue; }
      read -rp "参照画像のパス（out/ref/...）: " ref
      read -rp "どう合成する?（例: his hand cups her breast）: " ins
      "$PY" scripts/compose_still.py "$r" "$ref" "$ins"
      pause ;;
    5)
      echo; echo "対象:"; r=$(pick_raw)
      [ -n "$r" ] || { echo "画像がありません"; pause; continue; }
      read -rp "動き（例: she slowly exhales）: " mo
      "$PY" scripts/wan5b_i2v.py "$r" "$mo" --fast --frames 81
      pause ;;
    6)
      echo; echo "対象:"; r=$(pick_raw)
      [ -n "$r" ] || { echo "画像がありません"; pause; continue; }
      read -rp "動き（例: slow pelvic rocking）: " mo
      "$PY" scripts/wan14b_i2v.py "$r" "$mo"
      pause ;;
    7)
      echo; echo "--- ブロック ---"
      for f in $(find dist/blocks -name '*.md' 2>/dev/null | sort); do
        printf '%-34s %s\n' "$(basename "$f" .md)" "$(head -1 "$f" | sed 's/^# //')"
      done
      echo "--- 生成物 ---"; ls -1 $RAW 2>/dev/null | grep -E '^[0-9]{4}\.' || echo "(なし)"
      pause ;;
    8)
      echo; ls -1 $RAW 2>/dev/null | grep -E '^[0-9]{4}\.'
      read -rp "採用する番号（空白区切り）: " a
      [ -n "$a" ] && "$PY" scripts/promote.py $a
      read -rp "不採用にする番号（空白区切り・空でも可）: " rj
      [ -n "$rj" ] && "$PY" scripts/promote.py --reject $rj
      pause ;;
    9)
      "$PY" scripts/promote.py --list
      nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader 2>/dev/null \
        || "$PY" -c 'import torch;f,t=torch.cuda.mem_get_info();print("free",f//1048576,"MB")'
      pause ;;
    0) exit 0 ;;
  esac
done
