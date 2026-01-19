🧠 Project Dystopia: 画像生成資源化計画
「画像生成を『ギャンブル』から『設計』へ」

本リポジトリは、ComfyUIを用いた「高精度・高再現性」な画像生成パイプラインと、
それを操るための思想的インターフェース（PromptEngine）を提供します。

📖 聖典：四つの柱（Philosophy）
我々は、消費されるだけの「生成ガチャ」を拒絶する。

粒度の支配  
　AIのリソースは有限である。背景、構図、細部に優先順位をつけ、無駄な書き込みを排せ。

構造の継承  
　優れたポーズや構図は「資源」である。Type Eを用い、骨格を次の生成へと引き継げ。

局所の執着  
　全体を変えずに一部を磨く。Type D/D+は、あなたの「欲望（フェチ）」を純化するためのメスである。

資源の循環  
　生成は終わりではない。優れた出力は次の素材（Asset）となり、螺旋のようにクオリティを高めていく。

🛠 導入手順（RunPod / Private環境）
1. リポジトリの召喚
bash
git clone https://github.com/herorobot-boop/Project-Dystopia.git
cd Project-Dystopia
2. 環境の自動構築（Phase Vまで）
bash
python setup_sync_v50.py
✅ Pony, RealVisXL 5.0, FLUX等の主要モデルとカスタムノードが自動展開されます。

🕹 運用マニュアル：弾丸を込め、撃ち抜く
Step 1: 弾丸の精製（PromptEngine GUI）
🟢 手動設計モード（GUI v1）
bash
python interface_gradio_v1.py
キャラ・シーン・スタイル・LoRAタグを手動で入力

Positive / Negative Prompt を生成し、ComfyUIに貼り付けて使用

GUI起動後、表示されたURL（例：https://xxxx.gradio.live）をブラウザで開く

💡 Tip: Extra欄に [ANTI_MELT], [REAL_SKIN], [POSE_FIX] などのタグを活用

🔷 思想駆動モード（GUI v2）
bash
# 事前にローカルLLMを起動（初回のみ）
python setup_sync_llm.py

# GUI起動
python interface_gradio_v2.py
日本語で構成指示を入力するだけで、LLMが構造タグを生成

自動で prompt_*.json を構築し、ComfyUIで即実行可能

GUI起動後、表示されたURL（例：https://xxxx.gradio.live）をブラウザで開く

✅ .json は RunPayloads/ に保存されます

Step 2: 構造の展開（ComfyUI）
ComfyUIを開き、workflows/ 内の最適な「銃（JSON）」を読み込みます。

Type	用途
A / B / C	標準・実験・垂直整理。FLUX + Ponyのハイブリッド構成
D / D+	局所修正。特定部位を「資源化」レベルまで描き変える
E	骨格継承。ポーズを固定し、キャラクターを転生させる
Step 3: 装填と発射
GUIで生成した Positive Prompt を CLIP Text Encode ノードに貼り付け

.json を読み込んだ場合はそのまま実行ボタンを押すだけ

🧭 GUIの使い分けまとめ
あなたの目的	使うGUI	起動コマンド
自分で構成を細かく組みたい	interface_gradio_v1.py	python interface_gradio_v1.py
日本語で指示して自動生成したい	interface_gradio_v2.py	python interface_gradio_v2.py
ComfyUIに貼るだけのプロンプトが欲しい	GUI v1	✅
.json で構成を保存・再利用したい	GUI v2	✅
🔞 リミッター解除：検閲なき創造
Project Dystopiaは、外部の検閲サーバーを介しません。
Pony系モデルが持つ潜在的な表現力を、PromptEngineが自動で最適化し、
最高純度の「資源」へと変換します。

📂 フォルダ構成（抜粋）
コード
Project-Dystopia/
├── interface_gradio_v1.py        # 手動プロンプト設計GUI
├── interface_gradio_v2.py        # 思想駆動プロンプト生成GUI
├── prompt_engine_v1.py
├── prompt_engine_v2_chronos.py
├── chronos_mapper_v3_2.py
├── prompt_builder.py
├── setup_sync_llm.py             # RunPod用LLM起動スクリプト
├── RunPayloads/                  # 生成されたプロンプト保存先
├── mapped/                       # 構造タグ付きscene_code保存先
├── workflows/                    # ComfyUI用ワークフロー群
└── structure_tags.json           # タグ定義辞書
