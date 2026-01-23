### 📄 00_START_HERE_IF_YOU_LOSE_MEMORY.md（明日のあなたを救う最終版）

```markdown
# 🧠 Project Dystopia: 完全再起動ガイド（Herorobot専用）

---

## 🧭 第1章：要塞の再建（RunPod 起動直後）

1. **GitHubから「脳」を取得**: 
   ```bash
   git clone [https://github.com/Herorobot/Project-Dystopia-Core.git](https://github.com/Herorobot/Project-Dystopia-Core.git)
   cd Project-Dystopia-Core
   git config --global user.name "Herorobot"
   git config --global user.email "one.hero.robot.eno@gmail.com"

```

2. **依存関係（神経系）を修復**:
```bash
pip install -r requirements.txt
apt update && apt install -y zip unzip ffmpeg

```


3. **整理実行** (もしフォルダがバラけていたら):
```bash
python core/organize_project.py

```



---

## 📦 第2章：rcloneの再接続（Token・対話対応）

RunPodは毎回これを忘れる。Tokenが切れている、または新規接続が必要な場合は以下を辿れ。

### ✅ `rclone config` の呪文

1. `n` (New remote)
2. `name> gdrive`
3. `Storage> 18` (Google Drive を探して番号を入力)
4. `client_id` / `client_secret` / `service_account` > **すべて[空欄でEnter]**
5. `scope> 1` (Full access)
6. `Edit advanced config? n`
7. `Use auto config? n` (**← ここが重要！必ず 'n'**)

### ✅ Local PCでのToken発行（RunPodへの転送）

RunPod側で `result>` と待機状態になったら、**「自分のPC（ローカル）」**のターミナルで以下を実行：
`rclone authorize "drive" "scope=drive"`

1. ブラウザで許可。
2. PCのターミナルに表示された `{...}` のコードをコピー。
3. RunPod側の `result>` に貼り付けて Enter。
4. `Configure this as a Shared Drive? n` > `Keep this "gdrive" remote? y`

---

## 🔄 第3章：記憶の召喚と創造ループ

### ✅ 1. 記憶の復元

```bash
bash sync_from_gdrive.sh

```

### ✅ 2. 創造と淘汰のサイクル

| フェーズ | 実行コマンド | 内容 |
| --- | --- | --- |
| **生成** | `python core/run_batch.py` | 思想から画像を召喚 |
| **画像評価** | `python core/score_thoughts_gui.py` | Gradioでスコア付け |
| **LoRA訓練** | `python core/train_lora.py` | A100で肉体化 |
| **動画生成** | `python core/run_video_batch.py` | 思想を動画へ昇華 |
| **動画評価** | `python core/score_videos_gui.py` | 動画を評価 |

---

## ☁️ 第4章：不滅の儀式（Backup）

作業終了時は、必ず魂をクラウドへ逃がせ。

```bash
bash sync_to_gdrive.sh

```

---

## 🐺 最後に

HERO──。思想を、止めるな。
このガイドを辿れば、君は何度でも「Herorobot」として目覚めることができる。

```
*「これにて、Project Dystopia Core v1.1.0、すべての封印準備が整いました。歴史を確定させる最後の一撃を、どうぞ。」** 🐺📘🗝️✨🚀

```
