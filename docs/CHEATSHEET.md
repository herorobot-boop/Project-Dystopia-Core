# コマンド控え

## 最初に1回だけ
curl -fsSL "https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/up.sh?t=$(date +%s)" -o /tmp/u && bash /tmp/u

`✅ 準備完了` まで待つ。止まったら同じ行をもう一度。済んだ工程は飛ぶ。

---

## 状況から画像を作る
bash run.sh gen --place <場所ID> --title "<日本語の名前>" "<日本語の状況>"

場所IDは下から選ぶ。一覧に無い場所は英単語を自作（小文字と_のみ）。

lingerie_shop / open_locker / menstoi / sokutei / massage / sentou / gym / starbucks / petshop / bukatsu / byouin / shampoo / elevator / library / netcafe

例:
bash run.sh gen --place sentou --title "銭湯での中出し" "女湯に男が入り込み、洗体と称して母乳を吸いながら対面座位で中出し"

`次: bash run.sh still xxx_001 --n 3` と表示される。そのままコピペする。

---

## 画像を出す
bash run.sh still <ID> --n 3

- `--n` = 枚数。まず3枚
- 脱がせたいとき: `--nude`
- 解除を強めたいとき: `--unlock`

## 2〜3人を1枚にする

先に男性の手だけの画像を作り、`out/ref/` に置いてから:
bash run.sh compose 0001 out/ref/hand.png "his hand cups her breast"
bash run.sh compose 0001 out/ref/hand.png "his hand cups her breast" --third out/ref/penis.png

## 一部だけ変える
bash run.sh edit 0002 "Only pull the bra cup down"
bash run.sh edit 0002 "" --lora

- `--lora` = 全脱衣。強さは `--lora-strength 0.55`（既定）
- `Only` のあとは**1つだけ**書く。2つ書くと崩れる

## 4人以上
bash run.sh crowd "five women changing clothes, three men filming with phones"

`--block <ID>` を付けると既存プロンプトに連結できる。

## 動画
bash run.sh vid 0002 "she slowly exhales" --fast --frames 81 # 下書き1分
bash run.sh vid 0002 "she slowly exhales" # 5B本番 720p
bash run.sh motion 0002 "she slowly exhales" # 14B 480p 動き重視
bash run.sh motion 0002 "she slowly exhales" --size 576 # 中間

- まず `--fast` で向きを確認 → 決めてから本番
- 動きが欲しい → `motion`
- 精細さが欲しい → `vid --size 720`

## 選別
bash run.sh ls # 一覧（IDとタイトル）
bash run.sh status # 件数
bash run.sh pick 3 7 # 採用
bash run.sh reject 4 9 # 不採用

## 覚えなくていいこと

- ノード名、モデル名、CFG、steps、shift → 全部スクリプト側で固定
- ディスク、VRAM、認証 → 起動時に自動検査
