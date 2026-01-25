#!/bin/bash

# ==========================================================
# H-K9 COMMAND CENTER: HIGH-PERFORMANCE LAUNCHER (V2)
# Optimized for RTX 4090 / A100 / H100 (Blackwell Ready)
# ==========================================================

echo "🐺 [H-K9] Initiating Tactical Environment..."

# 1. パスの自動特定
PROJECT_ROOT=$(pwd)
COMFYUI_DIR="/workspace/ComfyUI"

# 2. GitHub 同期 & 競合ケア
# RunPod上の未コミットな変更がGitHub側と競合した場合の対策
echo "🐙 [H-K9] Synchronizing Intelligence from GitHub..."

# もし「強制的にGitHub側に合わせたい（競合を無視する）」場合は、
# 以下の git pull を git fetch --all && git reset --hard origin/main に書き換えてください。
git pull origin main || {
    echo "⚠️  [CONFLICT] Binary or code conflict detected."
    echo "💡 To force sync from GitHub (ERASE LOCAL CHANGES), run: 'git reset --hard origin/main'"
    echo "Continuing with current local state..."
}

# 3. GPU 最適化フラグの設定
# RTX 4090 / A100 等の演算性能を最大化
export CUDA_LAUNCH_BLOCKING=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# コンピューティング性能の自動判別（Blackwell/Hopper/Ada）
# 4090 (Compute 8.9), A100 (Compute 8.0)
export TORCH_CUDA_ARCH_LIST="8.0 8.6 8.9 9.0"

# 4. 資産の同期 (Gdrive -> Local)
echo "📦 [H-K9] Syncing assets from Gdrive..."
if [ -d "$PROJECT_ROOT/gdrive" ]; then
    python3 setup_models.py
else
    echo "❌ Error: Gdrive not mounted at $PROJECT_ROOT/gdrive"
    exit 1
fi

# 5. 依存関係の高速修復
echo "🛠️ [H-K9] Verifying dependencies..."
pip install -q pandas pathlib flask requests opencv-python-headless 
# 動画生成エンジンに必要な高速アテンションライブラリをチェック
pip install -q sageattention || echo "⚠️ SageAttention install failed - continuing..."

# 6. ComfyUI 起動ルーチン
# --bf16-storage: VRAM消費を抑え速度を向上
echo "🚀 [H-K9] Launching ComfyUI on Port 8188..."

cd $COMFYUI_DIR
python3 main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --bf16-storage \
    --use-split-cross-attention \
    --preview-method auto \
    --extra-model-paths-config "$PROJECT_ROOT/core/protocols/extra_model_paths.yaml" &

# 7. 思想エンジンのスタンバイ
cd $PROJECT_ROOT
echo "🧠 [H-K9] Thought Generator Engine: STANDBY"
echo "✅ Setup Complete. Access ComfyUI via RunPod Connect button."
echo "----------------------------------------------------------"
echo "To stop H-K9, use: 'pkill -f main.py'"
echo "To export results, use: 'python3 sync_to_gdrive.py'"
echo "To resolve Git conflicts, use: 'git reset --hard origin/main'"
