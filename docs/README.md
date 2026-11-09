# Project-Dystopia-Core

RunPod + ComfyUI で「日常の一幕をエロく切り取る」画像を作り、選んだものだけ動画化するための管理リポジトリ。

## 構成

| 場所 | 役割 |
|---|---|
| `data/catalog.tsv` | ネタ台帳。列をタブで区切った表。ここに全部書く |
| `data/scenarios/` | 台帳から変換されたYAML。手で書かない |
| `config/` | 抽選ルールと画風の共通設定 |
| `scripts/` | 変換・検品・生成・選別の道具 |
| `dist/` | 生成されたプロンプト。RunPodはここを読む |

## 作業順
python3 scripts/import_tsv.py # 台帳 → YAML
python3 scripts/validate.py # 検品。エラー0になるまで直す
python3 scripts/build.py # YAML → dist/blocks/*.md
bash scripts/sync.sh "追加" # コミットしてpush

## 1件だけ足したいとき
python3 scripts/new_scenario.py --engine E2 --place menstoi --title "混雑男トイレ"
python3 scripts/validate.py
python3 scripts/build.py

## 女優を抽選する
python3 scripts/roll_cast.py

出力された行をYAMLの `cast_note` に貼る。

## ルール

- 日本人80%、D〜Gカップ、赤面させない
- 表情は4型をランダム配分
- プロンプトは1行60語以内のタグ列挙。散文禁止
- 中出し・母乳は静止画では「抜いた後」しか描けないので動画前提
- 全数を動画化しない。`out/raw` から選別して `out/selected` だけ動画へ
