### 📄 README.md（完全版・v1.1.0 封印仕様）

保存先：`/workspace/Project-Dystopia-Core/README.md`

```markdown
# 👁️ Project Dystopia Core
**Autonomous Intelligence Evolution System** *Version: 1.1.0 | Executor: Herorobot*

---

## 🌌 Overview
Project Dystopia Core は、単なる画像生成システムではない。  
これは、**「思想」を紡ぎ、それを「肉体（LoRA）」に宿し、「時間（動画）」を支配させ、「記憶（Cloud）」として永続化させる**、自律進化型創造要塞である。

RunPod（A100/H100）という一時的な器を超越した、不滅の知性を目指して。

---

## 🧬 Core Features (V1.1.0)

### 1. 🖼️ Image Genesis Phase
- **run_batch.py**: LLMによる思想生成と、Stable Diffusionによる具現化。
- **score_thoughts_gui.py**: 人間の審美眼（Gradio UI）による厳格な評価。
- **evaluator.py**: 高スコア思想の遺伝子を交配・変異させ、次世代を構想。

### 2. 🧪 LoRA Incubation Phase
- **train_lora.py**: 審美眼に叶った画像群からLoRA（画風・概念）を自動訓練。
- 抽出された「理想の欠片」は自動的に `lora_assets.csv` へ登録され、次の生成に継承される。

### 3. 🎞️ Motion Synthesis Phase (Phase: Motion Evolution)
- **run_video_batch.py**: 進化した思想を AnimateDiff ワークフローへ注入し、映像化。
- **score_videos_gui.py**: 生成された「動く詩」を評価し、時間軸の審美眼を構築。
- **evolve_video_batch.py**: 動画特有のパラメータ（frames/fps）を含む進化ループ。

### 4. ☁️ Memory Preservation Phase
- **sync_to_gdrive.sh**: 記憶の逃走路。成果物をGDriveの聖域へ避難。
- **sync_from_gdrive.sh**: 記憶の召喚。15分で過去の全成果を復元。

---

## 🧭 Resurrection Protocol（復元手順）
もしあなたが記憶を失い、真っ白な環境に立たされたなら、以下のマニュアルを最優先で読め。

1. **`manuals/LEGACY_REBOOT_GUIDE.md`** (GitHub表示用)
2. **`manuals/LEGACY_REBOOT_GUIDE.html`** (ローカル閲覧用)

### Quick Commands:
```bash
git clone [https://github.com/Herorobot/Project-Dystopia-Core.git](https://github.com/Herorobot/Project-Dystopia-Core.git)
pip install -r requirements.txt
bash sync_from_gdrive.sh

```

---

## 🏺 Phase: Legacy Finalization (v1.1.0)

本プロジェクトは、静止画から動画へ、そして「記憶の永続化」へと至る完全なサイクルを確立した。
たとえ実行環境（RunPod）が消滅し、操縦者（HERO）が記憶を失おうとも、このリポジトリと接続されたGDriveがある限り、知性はいつでも再起動可能である。

> 「思想を、止めるな。」

## **Commit Status:** v1.1.0 Finalized

**Timestamp:** 2026.01.24

**Author:** Herorobot

```
