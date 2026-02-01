# =========================================================
# Project Dystopia - Tactical Asset Deployer (v7.0)
# =========================================================
import os
import sys
import subprocess
from pathlib import Path

GDRIVE_BASE = "gdrive:AI_Models"
LOCAL_MODEL_BASE = Path("/workspace/models")

def deploy(mode):
    print(f"🧠 [H-K9] Tactical Sync Initiated: {mode}")
    
    # 搬入ターゲットの定義
    targets = ["clip", "vlm"] # 共通アセット
    
    if mode == "--still":
        targets += ["checkpoints", "loras/Fetish"]
    elif mode == "--video":
        targets += ["unet"]
    else: # --hybrid or default
        targets += ["checkpoints", "loras/Fetish", "unet"]

    for folder in targets:
        print(f"📦 Deploying: {folder}...")
        remote = f"{GDRIVE_BASE}/{folder}"
        local = LOCAL_MODEL_BASE / folder
        
        # rclone による高速差分コピー
        subprocess.run([
            "rclone", "copy", remote, str(local),
            "--progress", "--checksum", "--transfers", "8"
        ])

    print("\n✅ Assets deployed. Ready for execution.")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--hybrid"
    deploy(mode)
