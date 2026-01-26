#!/bin/bash

# ==========================================================
# H-K9 COMMAND CENTER: SELF-EVOLVING LAUNCHER
# ==========================================================

echo "🐺 [H-K9] Initiating Self-Evolving Environment..."

# --- 準備工程 (省略/前述と同じ) ---
PROJECT_ROOT=$(pwd)
COMFYUI_DIR="/workspace/ComfyUI"
git reset --hard origin/main
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
pip install -q pandas pathlib flask requests opencv-python-headless sageattention xformers

# --- 起動とループ ---
echo "🚀 [H-K9] Launching ComfyUI & Inspector..."

# ComfyUIをバックグラウンド起動
cd $COMFYUI_DIR
python3 main.py --listen 0.0.0.0 --port 8188 --bf16-storage --extra-model-paths-config "$PROJECT_ROOT/core/protocols/extra_model_paths.yaml" > /dev/null 2>&1 &

cd $PROJECT_ROOT

# [重要] 自己進化ループの開始
# 生成 -> 判定 -> 修正 -> 再生成 を自動で回すモード
echo "🧠 [H-K9] Thought Generator: AUTO-EVOLUTION MODE"
echo "----------------------------------------------------------"
echo "AI will now inspect every generation against the Dictionary."
echo "----------------------------------------------------------"

# インタラクティブ兼、自動判定待機モードで起動
python3 core/engines/thought_generator.py --interactive --enable-inspection
