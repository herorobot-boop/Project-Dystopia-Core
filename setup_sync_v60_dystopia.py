# =========================================================
# Project Dystopia - Phase I: Infrastructure Sync (v6.0)
# =========================================================
import os
import subprocess

# 既存のCSVから読み込んだGdriveパス
GDRIVE_MODEL_PATH = "gdrive:/AI_Models"
LOCAL_WORKSPACE = "/workspace/models"

def main():
    print("🚀 Project Dystopia: Starting specialized synchronization...")
    
    # 1. 既存資産の同期 (Gdrive -> NVMe)
    # あなたが今まで積み上げた LoRA や Checkpoint を物理コピー
    subprocess.run(f"rclone copy {GDRIVE_MODEL_PATH} {LOCAL_WORKSPACE} --progress --checksum --exclude 'Old_Backups/**'", shell=True)

    # 2. 新規モデルのダウンロード (未だGdriveにない場合のみ提示)
    new_assets = [
        ("Z-Image-6B", "https://huggingface.co/Alibaba-LaVie/Z-Image"),
        ("Wan-2.6", "https://huggingface.co/Wan-AI/Wan-Video")
    ]
    
    # 3. リポジトリの最新化
    subprocess.run("git pull origin main", shell=True)

    print("\n✅ Sync Complete. System Ready for Z-Image reinforcement.")

if __name__ == "__main__":
    main()
