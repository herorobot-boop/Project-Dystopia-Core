#!/bin/bash
# ==========================================================
# H-K9 COMMAND CENTER: MISSION-BASED LAUNCHER (V7.0)
# ==========================================================

MODE=$1 # --still, --video, --hybrid, --logistics
PROJECT_ROOT="/workspace/Project-Dystopia-Core"
COMFYUI_DIR="/workspace/ComfyUI"

echo "🐺 [H-K9] Mission Mode: ${MODE:-'--hybrid (default)'}"

# 1. 環境最適化フラグ (Blackwell / 5090)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_CUDA_ARCH_LIST="9.0"

# 2. GitHub同期 (知能の最新化)
cd $PROJECT_ROOT && git fetch origin main && git reset --hard origin/main

# 3. モード別：ComfyUI起動引数の構築
case "$MODE" in
  "--still")
    # 画像生成特化：Z-Image / Flux 優先ロード
    ARGS="--nvfp4 --bf16-storage --highvram"
    echo "🎨 [STILL MODE] Focused on Z-Image 2048px development."
    ;;
  "--video")
    # 動画生成特化：Wan 2.6 / 32GB VRAMフル活用
    ARGS="--nvfp4 --bf16-storage --highvram --gpu-only"
    echo "🎬 [VIDEO MODE] Focused on Wan 2.6 Physical Dynamics."
    ;;
  "--logistics")
    # 兵站モード：ComfyUIは起動せず、モデル取得のみ
    echo "📦 [LOGISTICS MODE] Running fetch_new_models.py..."
    python3 core/utils/fetch_new_models.py
    exit 0
    ;;
  *)
    # ハイブリッド（デフォルト）：全モデル共存
    ARGS="--nvfp4 --bf16-storage --highvram"
    echo "⚖️ [HYBRID MODE] Full pipeline execution."
    ;;
esac

# 4. Command Center (tmux) 起動
tmux kill-session -t h_k9 2>/dev/null
tmux new-session -d -s h_k9

# 左パネル: ComfyUI
tmux send-keys -t h_k9 "cd $COMFYUI_DIR && python3 main.py --listen 0.0.0.0 --port 8188 $ARGS --extra-model-paths-config $PROJECT_ROOT/core/protocols/extra_model_paths.yaml" C-m

# 右パネル: 思想エンジン
tmux split-window -h -t h_k9
tmux send-keys -t h_k9 "cd $PROJECT_ROOT && python3 core/engines/thought_generator_v3.py" C-m

echo "✅ [H-K9] Deployment Complete. 'tmux a -t h_k9' to enter."
