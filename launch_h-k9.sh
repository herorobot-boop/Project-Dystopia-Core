#!/bin/bash

# ==========================================================
# H-K9 COMMAND CENTER: 5090 OPTIMIZED LAUNCHER
# ==========================================================

echo "🐺 [H-K9] Initiating Blackwell-5090 Tactical Environment..."

# 1. パスの自動特定
PROJECT_ROOT=$(pwd)
COMFYUI_DIR="/workspace/ComfyUI"

# 2. 5090 / CUDA 12.8 最適化フラグの設定
# Blackwellアーキテクチャの性能を最大化し、メモリ断片化を防止
export CUDA_LAUNCH_BLOCKING=0
export TORCH_CUDA_ARCH_LIST="9.0" # 5090/B200用
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# 3. 資産の同期 (Gdrive -> Local)
echo "📦 [H-K9] Syncing assets from Gdrive..."
python3 setup_models.py

# 4. 依存関係の高速修復 (5090環境で落ちやすいパッケージを再固定)
echo "🛠️ [H-K9] Verifying dependencies..."
pip install -q pandas pathlib flask requests opencv-python-headless 
# 動画生成エンジン(Hunyuan/Wan)に必要な高速アテンションライブラリをチェック
pip install -q sageattention || echo "⚠️ SageAttention install failed - continuing..."

# 5. ComfyUI 起動ルーチン
# --bf16-storage: 5090の演算性能を活かす
# --preview-method auto: 生成過程を可視化
echo "🚀 [H-K9] Launching ComfyUI on Port 8188..."

cd $COMFYUI_DIR
python3 main.py \
    --listen 0.0.0.0 \
    --port 8188 \
    --bf16-storage \
    --use-split-cross-attention \
    --preview-method auto \
    --extra-model-paths-config "$PROJECT_ROOT/core/protocols/extra_model_paths.yaml" &

# 6. 思想エンジンのスタンバイ
cd $PROJECT_ROOT
echo "🧠 [H-K9] Thought Generator Engine: STANDBY"
echo "✅ Setup Complete. Access ComfyUI via RunPod Connect button."
echo "----------------------------------------------------------"
echo "To stop H-K9, use: 'pkill -f main.py'"
echo "To export results, use: 'python3 sync_to_gdrive.py'"
