🧠 Project Dystopia: 画像生成資源化計画
「画像生成を『ギャンブル』から『設計』へ」

本リポジトリは、ComfyUIを用いた「高精度・高再現性」な画像生成パイプラインと、それを操るための「思想的インターフェース」を提供します。

📖 聖典：粒度の支配（Philosophy）
画像生成において、我々は消費されるだけの「ガチャ」を拒絶する。

第一章：粒度の支配 - AIのリソースは有限である。背景、構図、細部に優先順位をつけ、無駄な書き込みを排せ。

第二章：構造の継承 - 優れたポーズや構図は「資源」である。Type Eを用い、骨格を次の生成へと引き継げ。

第三章：局所の執着 - 全体を変えずに一部を磨く。Type D/D+は、あなたの「フェチ」を純化するためのメスである。

第四章：資源の循環 - 生成は終わりではない。優れた出力は次の生成の素材（Asset）となり、螺旋のようにクオリティを高めていく。

🛠 導入手順 (RunPod / Private環境)
1. リポジトリの召喚
RunPodのターミナルで以下を実行してください。

Bash

# 発行したトークンを使用してクローン
git clone https://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@github.com/herorobot-boop/Project-Dystopia.git
cd Project-Dystopia
2. 環境の自動構築
Bash

python setup_sync_v50.py
※Pony, RealVisXL 5.0, FLUX等の主要モデルとカスタムノードが自動で展開されます。

🕹 運用マニュアル：弾丸を込めて、撃つ
Step 1: 言葉の設計（PromptEngine GUI）
検閲なきローカル環境で「黄金のプロンプト」を精製します。

Bash

python interface_gradio.py
表示されたURLをブラウザで開く。

Typeを選択し、Extra欄にあなたの欲望（フェチ単語）を叩き込む。

※日本語でも入力可能ですが、英単語（例: wet latex, nipples through clothes）の方が爆発力が増します。

生成された Positive Prompt をコピー。

Step 2: 構造の展開（ComfyUI）
ComfyUIを開き、workflows/ フォルダ内の最適な「銃」を選択します。

Type A/B/C: 初動・実験・垂直整理。FLUX+Ponyのハイブリッド生成。

Type D/D+: 局所修正。既存画像を読み込み、マスクした部位のみを再錬成する。

Type E: 骨格継承。ポーズを固定し、中身だけを転生させる。

Step 3: 装填と発射
コピーしたプロンプトをComfyUIの CLIP Text Encode ノードに貼り付け、生成を開始してください。

🔞 リミッター解除：検閲なき創造
Project Dystopiaは、外部の検閲サーバーを介しません。 Pony系モデルが持つ潜在的な表現力を、PromptEngineが自動で最適化し、最高純度の「資源」へと変換します。

🧪 推奨LoRA・資源リスト
特定の質感やキャラクターを固定する場合、プロンプト末尾に <lora:名前:強度> を追記してください。

Detailed Skin/Texture: 肌のリアリティを極限まで高める（推奨: 0.6-0.8）

Latex/Glossy Style: 特定素材の反射を物理的に補正（推奨: 0.7-1.0）
