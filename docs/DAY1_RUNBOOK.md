# Day 1 実行手順

## Pod
- GPU: RTX 4090 / A100 どちらでも可
- コンテナディスク: **150GB以上**
- テンプレート: ComfyUI（/workspace/ComfyUI があるもの）
- ポート: 8188（HTTP）と 8888（Jupyter）を公開

## 起動後、Termius か Jupyter のターミナルで1行

curl -fsSL https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/scripts/provision.sh -o /tmp/p.sh && bash /tmp/p.sh

完了したら:

curl -fsSL https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/scripts/boot_omega.sh -o /tmp/b.sh && bash /tmp/b.sh

## 生成

python3 scripts/gen_still.py dist/blocks/e2/e2_menstoi_001.md --n 3
python3 scripts/edit_still.py Raw_e2_menstoi_001_00001_.png "Only pull the bra cup down" --lora
python3 scripts/wan5b_i2v.py Raw_e2_menstoi_001_00001_.png "she slowly exhales, slight shoulder movement"

## 選別

python3 scripts/promote.py --list
python3 scripts/promote.py 3 7
