# Day 1 実行手順

## Pod
- テンプレート: **ComfyUI**（必須。/workspace/ComfyUI が無いと provision が停止する）
- コンテナディスク: **150GB以上**
- 公開ポート: 8188、8888
- ネットワークボリューム: 今回は無し

## 手順（この順序を変えない）

### 1. 資材
curl -fsSL "https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/scripts/provision.sh?t=$(date +%s)" -o /tmp/p.sh && bash /tmp/p.sh
→ `✅ 資材完了`

### 2. 起動
curl -fsSL "https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/scripts/boot_omega.sh?t=$(date +%s)" -o /tmp/b.sh && bash /tmp/b.sh
→ `✅ 起動完了`

### 3. 生成（LLMは使わない場合ここから）
python3 scripts/gen_still.py dist/blocks/e2/e2_menstoi_001.md --n 3
python3 scripts/edit_still.py Raw_e2_menstoi_001_00001_.png "Only pull the bra cup down"
python3 scripts/edit_still.py Raw_e2_menstoi_001_00001_.png "" --lora --lora-strength 0.55
python3 scripts/wan5b_i2v.py Raw_e2_menstoi_001_00001_.png "she slowly exhales, slight shoulder movement"
下書き: python3 scripts/wan5b_i2v.py 入力.png "…" --fast
動きを増やす: --more-motion を足す

### 4. 選別
python3 scripts/promote.py --list
python3 scripts/promote.py 3 7
python3 scripts/promote.py --reject 4 9

## 新しいプロンプトを作るときだけ（VRAM衝突に注意）

### 5. LLM起動
curl -fsSL "https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/scripts/llm_server.sh?t=$(date +%s)" -o /tmp/l.sh && bash /tmp/l.sh
→ `✅ LLM起動`

### 6. プロンプト生成（8000番へ）

### 7. LLM停止（必須。8.3GBを空ける）
curl -fsSL "https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/scripts/llm_stop.sh?t=$(date +%s)" -o /tmp/s.sh && bash /tmp/s.sh
→ `✅ LLM停止`

### 8. 3. の生成へ戻る

## 画角
- パイズリ: 俯瞰
- 接触面: 真横接写
- 穴: 真横・胸高

## 出力先
/workspace/ComfyUI/output
