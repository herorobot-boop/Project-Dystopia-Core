### 📄 【決定版】00_START_HERE_IF_YOU_LOSE_MEMORY.md

保存先：`/workspace/Project-Dystopia-Core/manuals/00_START_HERE_IF_YOU_LOSE_MEMORY.md`

# 🧠 Project Dystopia: 完全再起動ガイド（Herorobot専用）

---

## 🧭 第1章：要塞の再建（RunPod 起動直後）

### ✅ 1. GitHubから「脳」を取得

```bash
git clone https://github.com/Herorobot/Project-Dystopia-Core.git
cd Project-Dystopia-Core

# Gitユーザー設定
git config --global user.name "Herorobot"
git config --global user.email "one.hero.robot.eno@gmail.com"

# git push時に聞かれたらこれを使え：
# Username: Herorobot
# Password: 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

```

### ✅ 2. 依存関係とツールの修復

```bash
pip install -r requirements.txt
apt update && apt install -y zip unzip ffmpeg

```

---

## 📦 第2章：rcloneの再接続（Google Drive）

RunPodはブラウザが動かない。以下の手順で**「手元のPC」**と連携して認証せよ。

### ✅ 1. 手元のPC（Windows/Mac）でトークン発行

PCのターミナルで以下のコマンドを実行（あなたのIDを埋め込み済み）：

```bash
rclone authorize "drive" "449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com" "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"

```

→ ブラウザで許可し、表示された `{"access_token":...}` をコピー。

### ✅ 2. RunPod側の設定

```bash
rclone config

```

1. `n` (New remote) -> `name: gdrive`
2. `Storage: 18` (Google Drive)
3. `client_id: 449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com`
4. `client_secret: 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`
5. `scope: 1` (Full access)
6. `service_account_file: [Enter]`
7. `Edit advanced config? n`
8. `Use auto config? n` (**←重要**)
9. `config_token> [PCでコピーしたトークンを貼り付け]`
10. `y` (Keep this remote) -> `q` (Quit)

---

## 🔄 第3章：記憶の召喚と運用

```bash
# 記憶をGDriveから復元
bash sync_from_gdrive.sh

# 運用コマンド（詳細はREADME参照）
python core/run_batch.py         # 生成
python core/score_thoughts_gui.py # 評価
python core/run_video_batch.py   # 動画化

```

---

## ☁️ 第4章：不滅の儀式（Backup）

**ログアウト前、必ず実行せよ。**

```bash
bash sync_to_gdrive.sh

```

---
