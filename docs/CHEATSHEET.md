# 控え（読むだけ。打たなくてよい）
## 最初の1回
curl -fsSL https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/up.sh?t=$(date +%s) -o /tmp/u  bash /tmp/u
`✅ 準備完了` まで待つ。止まったら同じ行をもう一度。済んだ工程は飛ぶ。

## 以後はこれだけ
bash menu.sh

番号を押して、聞かれたことに答えるだけ。引数は覚えなくてよい。

## menu.sh の流れ
1 → 場所を選び、名前と状況を日本語で書く（英語化は自動）
2 → 静止画。まず3枚。脱がせたいなら y
3 → 局部だけ変える。`Only ...` に1つだけ書く
4 → 2〜3人。先に out/ref/ に手だけの画像を用意
5 → 動画の下書き（1分）
6 → 動画の本番（10〜15分）
7 → 一覧
8 → 採用・不採用
9 → GPUと件数

## 保存先
/workspace/ComfyUI/output → 自動で out/raw/0001.png に移る
見るのは JupyterLab（Port 8888）の out/raw

## 覚えなくていいこと
モデル名、CFG、steps、shift、ノード名、ディスク、VRAM → 全部スクリプト側
