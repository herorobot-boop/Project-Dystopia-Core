#!/bin/bash
# ==========================================================
# H-K9 COMMAND CENTER: FINAL LAUNCHER (V6.2 - Blackwell/Z-Image)
# ==========================================================

echo "🐺 [H-K9] Initiating Tactical Environment for RTX 5090..."

# パスの定義
PROJECT_ROOT="/workspace/Project-Dystopia-Core"
COMFYUI_DIR="/workspace/ComfyUI"

# 1. ワークスペース移動とGitHub同期 (最新の知能を物理現像)
cd /workspace
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "🐙 [H-K9] Cloning Intelligence..."
    git clone https://github.com/herorobot-boop/Project-Dystopia-Core.git
fi
cd $PROJECT_ROOT
echo "🐙 [H-K9] Syncing latest code from main..."
git fetch origin main && git reset --hard origin/main

# 2. Blackwell最適化フラグの注入
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_CUDA_ARCH_LIST="9.0"
echo "⚡ Blackwell (Compute Capability 9.0) optimization engaged."

# 3. 依存関係の高速修復 (SageAttention/nvfp4環境用)
echo "🛠️ [H-K9] Verifying specialized dependencies..."
pip install -q pandas pathlib flask requests opencv-python-headless jq

# 4. tmux セッションの構築 (Command Center)
echo "🖥️ [H-K9] Constructing Command Center..."
tmux kill-session -t h_k9 2>/dev/null
tmux new-session -d -s h_k9

# 左パネル: ComfyUI 起動 (nvfp4 + bf16-storage による極限現像)
tmux send-keys -t h_k9 "cd $COMFYUI_DIR && python3 main.py --listen 0.0.0.0 --port 8188 --bf16-storage --nvfp4 --highvram --extra-model-paths-config $PROJECT_ROOT/core/protocols/extra_model_paths.yaml" C-m

# 右パネル: 思想エンジン (interactiveモード)
tmux split-window -h -t h_k9
tmux send-keys -t h_k9 "cd $PROJECT_ROOT && python3 core/engines/thought_generator_v3.py" C-m

# 完了通知
echo "✅ [H-K9] Deployment Complete."
echo "👉 Access Command Center: tmux a -t h_k9"
