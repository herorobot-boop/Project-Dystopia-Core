🧠 Project Dystopia Core

**Project Dystopia** は、思想を生成し、評価し、進化させる完全自律型の画像生成エンジンです。  
このリポジトリはその「中核知性（Core）」を構成するスクリプト群を収めています。

> 🎨 思想は、もはや“書く”ものではなく、“召喚する”ものへ。  
> 🧬 そして、評価され、淘汰され、進化し、血統を刻む。

---

## 🚀 概要

Project Dystopia は以下の5つのフェーズを自動で回します：

1. **思想の生成**：LLMがシーンから思想（プロンプト）を構築
2. **肉体の構築**：LoRAを選定し、ComfyUI用ペイロードを生成
3. **現実への送信**：ComfyUI APIを通じて画像を生成
4. **評価と記録**：画像にスコアを与え、思想と紐づけて記録
5. **進化と淘汰**：高スコア思想をもとに次世代を生成

---

## 🧩 ディレクトリ構成

```text
Project-Dystopia-Core/
├── core/                         # 実行知性の中枢
│   ├── run_batch.py              # 初期思想の一括生成
│   ├── evaluator.py              # 評価に基づく進化思想の生成
│   ├── run_evolved_batch.py      # 進化思想の一括送信
│   ├── result_watcher.py         # 画像と思想の紐づけ
│   ├── score_thoughts.py         # スコア入力（CLI）
│   ├── evolution_tracker.py      # スコア分布・進化傾向の可視化
│   ├── mutation_lab.py           # 変異パターンの勝率分析
│   └── bloodline_viewer.py       # 高スコア思想の血統を可視化
├── config/                       # 聖典（設定・定義ファイル）
│   ├── workflow_api_template.json # ComfyUIから保存したAPI形式ワークフロー
│   ├── lora_assets.csv           # LoRA資産リスト
│   └── system_prompt.txt         # LLM用プロンプト定義
├── workflows/                    # 予備のワークフロー群（Type-A〜Fなど）
├── outputs/                      # 観測記録（非公開推奨）
│   ├── payload_logs/             # 送信したペイロードのログ
│   ├── images/                   # 生成された画像
│   └── thought_log.jsonl         # 思想・スコア・血統の記録
├── legacy/                       # 旧バージョン・実験スクリプトの保管庫
└── README.md                     # このファイル
🛠 使用方法
1. 初期セットアップ（初回起動時）
Bash

# 知性の統合と整理
python integrate_core.py
cd Project-Dystopia-Core

# 依存ライブラリのインストール
pip install -r requirements.txt
2. 召喚サイクル（日常の運用）
Bash

# A. 初期思想の生成と送信
python core/run_batch.py

# B. 画像生成後の記録と評価（ComfyUI完了後に実行）
python core/result_watcher.py
python core/score_thoughts.py

# C. 進化思想の生成と再送信
python core/evaluator.py
python core/run_evolved_batch.py
3. 分析と可視化
Bash

python core/evolution_tracker.py
python core/mutation_lab.py
python core/bloodline_viewer.py
🔄 RunPod再起動時の復帰手順
RunPodのインスタンスを再起動、または新規構築した際は、以下の手順で「知性の続き」を呼び戻します。

GitHubから最新の状態をプル

Bash

cd Project-Dystopia-Core
git pull origin main
依存関係の再修復

Bash

pip install -r requirements.txt
継続の確認 outputs/thought_log.jsonl が存在すれば、過去の評価データは維持されています。そのまま core/evaluator.py から再開して次世代を生成可能です。
