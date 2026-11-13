# Pod 専用コマンド（起動後だけ）

## 起動したら最初にやる
curl -fsSL https://raw.githubusercontent.com/herorobot-boop/Project-Dystopia-Core/main/up.sh?t=$(date +%s) -o /tmp/u  bash /tmp/u

止まったら**同じ行をもう一度**。済んだ工程は飛ぶ。

## 準備完了のあと
bash menu.sh

## 監査だけ走らせる
bash scripts/audit_all.sh

## ディスクを空ける（初回の1回だけ）
rm -f /workspace/ComfyUI/models/checkpoints/fluxed_up_5.1_fp8.safetensors
df -h /workspace

## 使わない土台に戻す（2511 → 2509）
mv /workspace/ComfyUI/models/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors /workspace/models/ 2>/dev/null

## 2511 を戻す
mv /workspace/models/qwen_image_edit_2511_fp8mixed.safetensors /workspace/ComfyUI/models/diffusion_models/ 2>/dev/null

## スマホ閲覧（menu の 10 でも可）
bash scripts/start_smart_gallery.sh
→ http://<pod-id>-8080.proxy.runpod.net

## ログ
tail -n 40 "$(ls -t /workspace/logs/comfy_*.log | head -1)"

## 状態
bash scripts/promote.py --list
nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
