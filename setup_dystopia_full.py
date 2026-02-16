# =========================================================
# Project Dystopia - Phase I: Final Infrastructure (v7.3)
# =========================================================
import os
import subprocess
from pathlib import Path

GDRIVE_MODEL_PATH = "gdrive:/AI_Models"
LOCAL_WORKSPACE = "/workspace/models"
COMFYUI_PATH = "/workspace/ComfyUI"

def run_command(cmd):
    print(f"[*] Executing: {cmd}")
    subprocess.run(cmd, shell=True)

def setup_env():
    print("🚀 Project Dystopia: Starting Final Integration Setup v7.3...")

    # 1. ディレクトリ確保
    for sub in ["checkpoints", "loras", "unet/wan2.2", "vae", "clip"]:
        os.makedirs(os.path.join(LOCAL_WORKSPACE, sub), exist_ok=True)

    # 2. 必須ライブラリの一括インストール (API / WebSocket / Image用)
    print("[*] Installing core python libraries...")
    run_command("pip install requests websocket-client pillow pandas opencv-python-headless originote-sdk")

    # 3. 高速同期 (Fast Mode)
    run_command(f"rclone copy {GDRIVE_MODEL_PATH} {LOCAL_WORKSPACE} --progress --update --size-only --transfers 16")

    # 4. 依存カスタムノードの「徴用」 (NotebookLM指摘分を網羅)
    nodes = [
        "https://github.com/ltdrdata/ComfyUI-Manager.git",
        "https://github.com/Kijai/ComfyUI-WanVideoWrapper.git",
        "https://github.com/civitai/sd_civitai_extension.git", # Civitai-Helper
        "https://github.com/pythongosssss/ComfyUI-WD14-Tagger.git",
        "https://github.com/LucianoCirino/efficiency-nodes-comfyui.git",
        "https://github.com/Mel-Anine/ComfyUI-VideoHelperSuite.git",
        "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git" # 検体固定用追加
    ]
    for repo in nodes:
        name = repo.split("/")[-1].replace(".git", "")
        path = os.path.join(COMFYUI_PATH, f"custom_nodes/{name}")
        if not os.path.exists(path):
            run_command(f"git clone {repo} {path}")
            if os.path.exists(f"{path}/requirements.txt"):
                run_command(f"pip install -r {path}/requirements.txt")

    # 5. リポジトリ最新化
    run_command("git pull origin main")

    print("\n✅ 武装完了。launch_h-k9.sh でComfyUIを起動してください。")

if __name__ == "__main__":
    setup_env()
