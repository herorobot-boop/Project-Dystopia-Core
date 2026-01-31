# =========================================================
# Project Dystopia: Infrastructure Setup Engine
# GitHub Repository: [User's Repo Name]
# Target Path: /workspace/
# =========================================================

import os
import subprocess

# ---------------------------------------------------------
# 1. 構成定義 (NotbookLM用マニュアル)
# ---------------------------------------------------------
# [RunPod NVMe Path]             [Gdrive Source Path]
# /workspace/models/checkpoints  <- gdrive:Models/Checkpoints
# /workspace/models/loras        <- gdrive:Models/Loras
# /workspace/models/unet         <- gdrive:Models/Unet (Wan 2.6)
# ---------------------------------------------------------

MODEL_BASE = "/workspace/models"
GDRIVE_REMOTE = "gdrive:/ProjectDystopia/models"

# 初回ダウンロードが必要な最新モデルリスト (手動用URL付)
NEW_MODELS = {
    "Z-Image-6B": {
        "url": "https://huggingface.co/Alibaba-LaVie/Z-Image",
        "dest": f"{MODEL_BASE}/checkpoints/zimage_6b.safetensors"
    },
    "Wan-2.6-T2V-14B": {
        "url": "https://huggingface.co/Wan-AI/Wan2.1-T2V-14B", # 2.6発表前は2.1最新版
        "dest": f"{MODEL_BASE}/unet/wan26_t2v_14b.safetensors"
    }
}

def setup_directories():
    paths = ["checkpoints", "loras", "unet", "vae", "vlm", "custom_nodes/dystopia_bridge"]
    for p in paths:
        os.makedirs(os.path.join(MODEL_BASE, p), exist_ok=True)
    print("✅ Local directories initialized.")

def sync_models():
    """GdriveからNVMeへの物理コピー実行"""
    print("🚀 Starting sync from Gdrive to NVMe...")
    # rclone copy で物理コピー。整合性チェック。
    subprocess.run(f"rclone copy {GDRIVE_REMOTE} {MODEL_BASE} --progress --checksum", shell=True)

def main():
    setup_directories()
    sync_models()
    
    print("\n⚠️  [Manual Download List] 初回のみGdriveへ手動搬入が必要な場合:")
    for name, info in NEW_MODELS.items():
        if not os.path.exists(info["dest"]):
            print(f"- {name}: {info['url']}")

if __name__ == "__main__":
    main()
