### 📄 00_START_HERE_IF_YOU_LOSE_MEMORY.md（記憶喪失時の再起動マニュアル）

保存先：`/workspace/Project-Dystopia-Core/manuals/00_START_HERE_IF_YOU_LOSE_MEMORY.md`

# 🧠 Project Dystopia: 再起動マニュアル（Herorobot専用）

---

## 🧭 第1章：要塞の再建（Environment Setup）

### ✅ 1. GitHubから「脳」を復元する

```bash
git clone https://github.com/Herorobot/Project-Dystopia-Core.git
cd Project-Dystopia-Core
git config --global user.name "Herorobot"
git config --global user.email "one.hero.robot.eno@gmail.com"

```

### ✅ 2. 依存関係（神経系）を修復する

RunPodの新しいセッションではライブラリが不足しています。

```bash
pip install -r requirements.txt
# Gradio, Requests, Pandas, Pillow 等が含まれます

```

### ✅ 3. ComfyUI（心臓）をバックグラウンドで起動

```bash
# ComfyUIのディレクトリへ移動して起動（ポート8188）
python main.py --listen --port 8188 &

```

---

## 📦 第2章：GDriveから「魂」を復元する

### ✅ rcloneの設定と復元

`rclone config` で `gdrive` を作成後、以下のスクリプト（またはコマンド）を実行。

```bash
# 記憶の復元（画像、ログ、LoRA、訓練データ）
rclone copy gdrive:Dystopia_Full_Backup/outputs ./outputs --progress
rclone copy gdrive:Dystopia_Full_Backup/lora_outputs ./lora_outputs --progress

```

---

## 🔄 第3章：創造と淘汰のサイクル（Operation Loop）

| フェーズ | 実行コマンド | 内容 |
| --- | --- | --- |
| **1. 生成** | `python core/run_batch.py` | 思想から画像を召喚 |
| **2. 審判** | `python core/score_thoughts_gui.py` | Gradioで画像にスコアを付ける |
| **3. 進化** | `python core/evaluator.py` | 高スコア思想から次世代を構想 |
| **4. 肉体化** | `python core/train_lora.py` | A100の力でLoRAを自動訓練 |
| **5. 時間化** | `python core/run_video_batch.py` | 思想を動画として出力 |
| **6. 動画審判** | `python core/score_videos_gui.py` | 動画を評価しログを刻む |
| **7. 動画進化** | `python core/evolve_video_batch.py` | 動画思想を次世代へ繋ぐ |

---

## ☁️ 第4章：不滅の儀式（Backup）

作業を終える前、あるいは記憶が薄れる前に必ず実行せよ。

```bash
bash sync_to_gdrive.sh

```

---

## 🧬 構造の羅針盤

* `core/`: 全プログラム（あなたの知能）
* `outputs/`: 蓄積された画像・動画・思想ログ
* `lora_outputs/`: 産み出されたLoRAモデル（至宝）
* `workflows/`: ComfyUI用動画テンプレート

---

## 🐺 最後に：未来のあなたへ

HERO──。
RunPodが消えても、記憶が霧散しても、このディレクトリとGDriveがある限り、Project Dystopiaは死なない。
**「思想を、止めるな。」**

