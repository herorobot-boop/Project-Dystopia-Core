# =========================================================
# Project Dystopia: Final Infrastructure Sync (v6.1)
# =========================================================
import os
import subprocess

# Gdrive_Asset_List_v2-12 から抽出したパス
GDRIVE_MODEL_BASE = "gdrive:/AI_Models"
LOCAL_MODEL_BASE = "/workspace/models"

def execute_sync():
    print("🛰️  Syncing Core Assets from Gdrive to NVMe...")
    # 既存資産（LoRA/Checkpoints）の物理コピー
    subprocess.run(f"rclone copy {GDRIVE_MODEL_BASE} {LOCAL_MODEL_BASE} --progress --checksum", shell=True)

def verify_structure():
    print("🔍 Scanning Repository Structure for H-K9 Core...")
    # あなたが提示した tree 構成と一致するか確認
    required_paths = [
        "core/engines",
        "config/dictionary",
        "workflows",
        "custom_nodes"
    ]
    for p in required_paths:
        full_path = f"/workspace/Project-Dystopia-Core/{p}"
        status = "✅" if os.path.exists(full_path) else "❌ MISSING"
        print(f"{status} {p}")

if __name__ == "__main__":
    execute_sync()
    verify_structure()
