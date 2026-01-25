#!/bin/bash

# ==========================================================
# H-K9 COMMAND CENTER: FINAL LAUNCHER
# Optimized for RTX 4090 / 6000 Ada / A100 / H100
# ==========================================================

echo "🐺 [H-K9] Initiating Blackwell-Class Environment..."

# 1. パスの自動特定
PROJECT_ROOT=$(pwd)
COMFYUI_DIR="/workspace/ComfyUI"

# 2. GitHub 同期（競合時はGitHubのコードを優先）
echo "🐙 [H-K9] Pulling latest logic from GitHub..."
git fetch origin main
git reset --hard origin/main

# 3. GPU/CUDA 最適化フラグ
export CUDA_LAUNCH_BLOCKING=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_CUDA_ARCH_LIST="8.0 8.6 8.9 9.0"

# 4. ディレクトリ構成の最終防衛
mkdir -p $PROJECT_ROOT/inputs/refer_images
mkdir -p $PROJECT_ROOT/outputs/images
mkdir -p $PROJECT_ROOT/core/protocols

# 5. 資産の同期 (Gdrive -> Local)
echo "📦 [H-K9] Syncing assets from Gdrive..."
if [ -d "$PROJECT_ROOT/gdrive" ]; then
    python3 setup_models.py
else
    echo "⚠️  Gdrive not detected at $PROJECT_ROOT/gdrive. Mounting check required."
fi

# 6. 依存関係の高速修復
echo "🛠️ [H-K9] Verifying dependencies..."
pip install -q pandas pathlib flask requests opencv-python-headless sageattention xformers

# 7. ComfyUI 起動 (バックグラウンド)
echo "🚀 [H-K9] Launching ComfyUI Node..."
cd $COMFYUI_DIR
python3 main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --bf16-storage \
    --use-split-cross-attention \
    --preview-method auto \
    --extra-model-paths-config "$PROJECT_ROOT/core/protocols/extra_model_paths.yaml" > /workspace/comfy_server.log 2>&1 &

# 8. 思想エンジン起動（インタラクティブモード）
echo "🧠 [H-K9] Thought Generator: ONLINE"
echo "----------------------------------------------------------"
echo "SYSTEM STATUS: READY FOR MISSION"
echo "Commands: 改01 - 改10 (KAI-Series) / シチュエーション指定"
echo "----------------------------------------------------------"

cd $PROJECT_ROOT
# LLMとの対話インターフェースを開始
python3 core/engines/thought_generator.py --interactive
