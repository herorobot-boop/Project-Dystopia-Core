#!/bin/bash
# ==========================================================
# H-K9 COMMAND CENTER: MISSION-BASED LAUNCHER (V7.3 FINAL)
# ==========================================================

MODE=$1 # --still, --video, --hybrid, --logistics
PROJECT_ROOT="/workspace/Project-Dystopia-Core"
COMFYUI_DIR="/workspace/ComfyUI"

# 0. 権限とディレクトリの強制解決（RunPod特有のバグ回避）
chmod +x $0
mkdir -p /workspace/outputs/images /workspace/outputs/video

echo "🐺 [H-K9] Mission Mode: ${MODE:-'--hybrid (default)'}"

# 1. 環境最適化フラグ (Blackwell / 5090 / 2026規格)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_CUDA_ARCH_LIST="9.0"

# 2. GitHub同期 (知能の最新化)
cd $PROJECT_ROOT && git fetch origin main && git reset --hard origin/main

# 3. モード別：ComfyUI起動引数の構築
# NotebookLM指摘の --enable-cors-header を標準搭載し、API接続拒否を根絶
BASE_ARGS="--listen 0.0.0.0 --port 8188 --enable-cors-header --extra-model-paths-config $PROJECT_ROOT/core/protocols/extra_model_paths.yaml"

case "$MODE" in
  "--still")
    ARGS="$BASE_ARGS --nvfp4 --bf16-storage --highvram"
    echo "🎨 [STILL MODE] Focused on Z-Image 2048px development."
    ;;
  "--video")
    # Wan 2.2 / 32GB VRAMフル活用 (2.6は商用制限のため2.2へ固定)
    ARGS="$BASE_ARGS --nvfp4 --bf16-storage --highvram --gpu-only"
    echo "🎬 [VIDEO MODE] Focused on Wan 2.2 Physical Dynamics."
    ;;
  "--logistics")
    echo "📦 [LOGISTICS MODE] Running setup_dystopia_full.py v7.3..."
    python3 setup_dystopia_full.py
    exit 0
    ;;
  *)
    ARGS="$BASE_ARGS --nvfp4 --bf16-storage --highvram"
    echo "⚖️ [HYBRID MODE] Full pipeline execution."
    ;;
esac

# 4. Command Center (tmux) 起動
tmux kill-session -t h_k9 2>/dev/null
tmux new-session -d -s h_k9

# 左パネル: ComfyUI (APIポート開放状態でバックグラウンド起動)
tmux send-keys -t h_k9 "cd $COMFYUI_DIR && python3 main.py $ARGS" C-m

# 右パネル: 思想エンジン待機 (Main.py 実行準備)
tmux split-window -h -t h_k9
tmux send-keys -t h_k9 "cd $PROJECT_ROOT && echo '🏛️ H-K9 READY. Run [python3 Main.py] to execute mission.'" C-m

echo "✅ [H-K9] Deployment Complete. 'tmux a -t h_k9' to enter."
