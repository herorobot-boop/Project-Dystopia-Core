🛠️ 執行：Project Dystopia "Genesis v7" 再構築プロトコル
# =========================================================
# H-K9 PROJECT: GENESIS SET-UP v7.5 [BLACKWELL OPTIMIZED]
# =========================================================
import os, subprocess, shutil, sys

# --- 物理定数・認証情報の定義 ---
GITHUB_TOKEN = "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"
GITHUB_REPO = "herorobot-boop/Project-Dystopia-Core"
RCLONE_CLIENT_ID = "449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com"
RCLONE_CLIENT_SECRET = "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"

# 1. GitHub 知能同期（認証プロンプトを物理排除）
def sync_intel():
    print("🐺 [1/4] 知能の同期を開始...")
    target_path = "/workspace/Project-Dystopia-Core"
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    subprocess.run(f"git clone {url} {target_path}", shell=True)
    print("✅ Intelligence synchronized.")

# 2. Rclone 自動構成（FUSEエラーを回避する物理コピー・プロトコル）
def setup_logistics():
    print("📦 [2/4] 兵站（Rclone）の自動構成...")
    config_content = f"""[gdrive]
type = drive
client_id = {RCLONE_CLIENT_ID}
client_secret = {RCLONE_CLIENT_SECRET}
scope = drive
"""
    config_path = os.path.expanduser("~/.config/rclone/rclone.conf")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        f.write(config_content)
    
    # 物理搬入執行：GdriveからNVMeへ (size-only で高速化)
    print("[*] Gdrive資産を爆速搬入中 (15分執行モード)...")
    local_models = "/workspace/models"
    os.makedirs(local_models, exist_ok=True)
    subprocess.run(["rclone", "copy", "gdrive:AI_Models", local_models, "--progress", "--update", "--size-only", "--transfers", "16"])

# 3. 脳（LLM）と肉体（Wan 2.2）の欠損補填
def repair_organs():
    print("🧠 [3/4] 脳（LLM）と肉体の整合性チェック...")
    # LLM (Abliterated-Llama-3)
    llm_dest = "/workspace/models/vlm/Abliterated-Llama-3.gguf"
    if not os.path.exists(llm_dest):
        print("[!] LLM missing. Fetching from backup...")
        url = "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-Abliterated-v3-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Abliterated-v3-Q8_0.gguf"
        subprocess.run(f"wget -O {llm_dest} {url}", shell=True)
    
    # Wan 2.2 (14B-FP8)
    wan_dest = "/workspace/models/unet/wan2.2_i2v_14B_fp8.safetensors"
    if not os.path.exists(wan_dest):
        print("[!] Wan 2.2 missing. Fetching core engine...")
        url = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_14B_fp8.safetensors"
        subprocess.run(f"wget -c {url} -O {wan_dest}", shell=True)

# 4. 点火：Blackwell 最適化起動（tmux）
def ignite_system():
    print("🚀 [4/4] システム点火準備 (Blackwell nvfp4)...")
    # extra_model_paths.yaml の生成
    os.makedirs("/workspace/Project-Dystopia-Core/core/protocols", exist_ok=True)
    with open("/workspace/Project-Dystopia-Core/core/protocols/extra_model_paths.yaml", "w") as f:
        f.write("comfyui:\n    base_path: /workspace/models\n    checkpoints: checkpoints/\n    loras: loras/\n    vae: vae/\n    clip: clip/\n    unet: unet/")

    # 起動コマンド（バックグラウンド）
    launch_script = """#!/bin/bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
tmux kill-session -t h_k9 2>/dev/null
tmux new-session -d -s h_k9
tmux send-keys -t h_k9 "cd /workspace/ComfyUI && python3 main.py --listen 0.0.0.0 --port 8188 --nvfp4 --bf16-storage --extra-model-paths-config /workspace/Project-Dystopia-Core/core/protocols/extra_model_paths.yaml" C-m
tmux split-window -h -t h_k9
tmux send-keys -t h_k9 "cd /workspace/Project-Dystopia-Core && python3 Main.py" C-m
"""
    with open("/workspace/launch_h_k9.sh", "w") as f:
        f.write(launch_script)
    os.chmod("/workspace/launch_h_k9.sh", 0o755)
    subprocess.run("/workspace/launch_h_k9.sh", shell=True)
    print("\n✅ [H-K9] 執行開始。'tmux a -t h_k9' で司令室に入ってください。")

if __name__ == "__main__":
    sync_intel()
    setup_logistics()
    repair_organs()
    ignite_system()
