### 📄 【決定版・改】01_START_HERE_IF_YOU_LOSE_MEMORY.md

保存先：`/workspace/Project-Dystopia-Core/manuals/00_START_HERE_IF_YOU_LOSE_MEMORY.md`

# 🧠 Project Dystopia: 完全再起動ガイド（Herorobot専用）

---

## 🧭 第1章：要塞の再建（RunPod 起動直後）

### ✅ 1. GitHubから「心臓部」を取得

```bash
git clone https://github.com/Herorobot/Project-Dystopia-Core.git
cd Project-Dystopia-Core

# Gitユーザー設定（これを行わないとpushできない）
git config --global user.name "Herorobot"
git config --global user.email "one.hero.robot.eno@gmail.com"

```

### ✅ 2. モデルの復元（重要：Gdriveから呼び出し）

※初回のみ、Gdriveへモデルをアップロードしておく必要があります（第4章参照）。

```bash
# rclone設定後、Gdriveからモデルをworkspaceへ高速転送
rclone copy gdrive:Project-Dystopia/models/llm /workspace/models/llm -P
rclone copy gdrive:Project-Dystopia/models/checkpoints /workspace/ComfyUI/models/checkpoints -P

```

---

## 📦 第2章：rcloneの再接続（Google Drive）

### ✅ 1. 手元のPCでトークン発行

PCのターミナルで実行：

```bash
.\rclone authorize "drive" "449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com" "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"

```

### ✅ 2. RunPod側の `rclone config`

設定値は以前と同様（client_id, secretを入力し、`Use auto config? n` でトークンを貼り付け）。

---

## 🚀 第3章：「120点の真実」起動プロトコル

本日のトライアンドエラーで到達した「最強の設定」を即座に再現する手順。

### ✅ 1. ポート解放と脳の覚醒

```bash
# 古いプロセスを殺す
kill -9 $(lsof -t -i:8000)

# Abliteratedモデルの起動
python3 -m llama_cpp.server --model /workspace/models/llm/Abliterated-Llama-3.gguf --port 8000 --n_gpu_layers -1

```

### ✅ 2. 執行スクリプトの実行（120点・黄金律モード）

```bash
python3 /workspace/Project-Dystopia-Core/talk_to_chronos.py

```

**※基準設定（自動適用済み）:**

* **Model**: `lustifySDXLNSFW_ggwpV7`
* **Steps**: 40-50 / **Sampler**: `dpmpp_2m_sde_gpu` / **Scheduler**: `karras`
* **Quality Tags**: `score_9, score_8_up, (photorealistic:1.4), (extremely detailed skin:1.3)`

---

## ☁️ 第4章：不滅の儀式（Backup & GitHub整理）

**作業終了時、またはGitHubを整理したい時に必ず実行せよ。**

### ✅ 1. LLMモデルをGdriveへ初バックアップ

Runpod上でダウンロードした大きなモデルをGdriveへ移します。

```bash
rclone copy /workspace/models/llm gdrive:Project-Dystopia/models/llm -P

```

### ✅ 2. GitHubへの整理とプッシュ

```bash
git add .
git commit -m "Update: H-K9 Protocol and 120pt quality settings"
git push origin main
# 認証情報を聞かれたらマニュアル第1章のPATを使用

```

### ✅ 3. 全データの同期

```bash
bash sync_to_gdrive.sh

```

---
