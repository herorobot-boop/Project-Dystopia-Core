Markdown

# 🧠 Project Dystopia: 画像生成資源化計画

「画像生成を『ギャンブル』から『設計』へ」

本リポジトリは、ComfyUIを用いた「高精度・高再現性」な画像生成パイプラインと、それを操るための「思想的インターフェース」を提供します。

---

## 📖 聖典：四つの柱（Philosophy）

我々は、消費されるだけの「生成ガチャ」を拒絶する。

1. **第一章：粒度の支配** - AIのリソースは有限である。背景、構図、細部に優先順位をつけ、無駄な書き込みを排せ。
2. **第二章：構造の継承** - 優れたポーズや構図は「資源」である。Type Eを用い、骨格を次の生成へと引き継げ。
3. **第三章：局所の執着** - 全体を変えずに一部を磨く。Type D/D+は、あなたの「欲望（フェチ）」を純化するためのメスである。
4. **第四章：資源の循環** - 生成は終わりではない。優れた出力は次の素材（Asset）となり、螺旋のようにクオリティを高めていく。

---

## 🛠 導入手順 (RunPod / Private環境)

### 1. リポジトリの召喚
RunPodのターミナルで以下を実行してください。
```bash
# 発行したトークンを使用してクローン
git clone [https://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@github.com/herorobot-boop/Project-Dystopia.git](https://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@github.com/herorobot-boop/Project-Dystopia.git)
cd Project-Dystopia
2. 環境の自動構築
Bash

python setup_sync_v50.py
※Pony, RealVisXL 5.0, FLUX等の主要モデルとカスタムノードが自動展開されます。

🕹 運用マニュアル：弾丸を込め、撃ち抜く
Step 1: 弾丸の精製（PromptEngine GUI）
検閲なきローカル環境で「黄金のプロンプト」を設計します。

Bash

python interface_gradio.py
表示されたURL（https://xxxx.gradio.live）をブラウザで開く。

Typeを選択し、Extra欄に欲望（フェチ単語）を叩き込む。

※OpenAIの制限を突破する「生の単語」が、Pony用の黄金構文に変換されます。

生成された Positive Prompt をコピー。

Step 2: 構造の展開（ComfyUI）
ComfyUIを開き、workflows/ 内の最適な「銃（JSON）」を読み込みます。

Type A/B/C: 標準・実験・垂直整理。FLUX+Ponyのハイブリッド。

Type D/D+: 局所修正。特定部位を「資源化」レベルまで描き変える。

Type E: 骨格継承。ポーズを固定し、キャラクターを転生させる。

Step 3: 装填と発射
コピーしたプロンプトを ComfyUI の CLIP Text Encode ノードに貼り付け、実行してください。

🔞 リミッター解除：検閲なき創造
Project Dystopiaは、外部の検閲サーバーを介しません。 Pony系モデルが持つ潜在的な表現力を、PromptEngineが自動で最適化し、最高純度の「資源」へと変換します。
