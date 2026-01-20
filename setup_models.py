import os
import shutil
from datetime import datetime

# モデルカテゴリと対応するGDriveパス
MODEL_CATEGORIES = {
    "Checkpoints": "gdrive/MyDrive/Project-Dystopia/models/Checkpoints",
    "LoRA": "gdrive/MyDrive/Project-Dystopia/models/LoRA",
    "VAE": "gdrive/MyDrive/Project-Dystopia/models/VAE",
    "Clip": "gdrive/MyDrive/Project-Dystopia/models/Clip",
    "Unet": "gdrive/MyDrive/Project-Dystopia/models/Unet",
    "Embeddings": "gdrive/MyDrive/Project-Dystopia/models/Embeddings",
    "ADetailer": "gdrive/MyDrive/Project-Dystopia/models/ADetailer",
    "RunPayloads": "gdrive/MyDrive/Project-Dystopia/RunPayloads",
    "Outputs": "gdrive/MyDrive/Project-Dystopia/outputs",
    "Logs": "gdrive/MyDrive/Project-Dystopia/run_log.csv"
}

# ComfyUIのモデル配置先
COMFYUI_MODEL_BASE = "/workspace/models"
COMFYUI_PAYLOADS = "/workspace/gdrive/MyDrive/Project-Dystopia/RunPayloads"
COMFYUI_OUTPUTS = "/workspace/gdrive/MyDrive/Project-Dystopia/outputs"

def sync_model_category(category, src_path, dst_base):
    dst_path = os.path.join(dst_base, category)
    os.makedirs(dst_path, exist_ok=True)

    if not os.path.exists(src_path):
        print(f"[{category}] ⚠️ Source path not found: {src_path}")
        return

    copied = 0
    for filename in os.listdir(src_path):
        src_file = os.path.join(src_path, filename)
        dst_file = os.path.join(dst_path, filename)
        if not os.path.exists(dst_file):
            shutil.copy2(src_file, dst_file)
            copied += 1
    print(f"[{category}] ✅ Synced {copied} new files to {dst_path}")

def main():
    print("🧠 [setup_models.py] Starting model sync...")
    print(f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for category, src in MODEL_CATEGORIES.items():
        if category in ["RunPayloads", "Outputs"]:
            # これらは ComfyUI のワークスペースに直接同期
            dst = COMFYUI_PAYLOADS if category == "RunPayloads" else COMFYUI_OUTPUTS
            os.makedirs(dst, exist_ok=True)
            if os.path.isdir(src):
                for filename in os.listdir(src):
                    src_file = os.path.join(src, filename)
                    dst_file = os.path.join(dst, filename)
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
                print(f"[{category}] ✅ Synced to {dst}")
            else:
                print(f"[{category}] ⚠️ Source path not found: {src}")
        elif category == "Logs":
            if os.path.exists(src):
                dst = os.path.join("/workspace", "run_log.csv")
                shutil.copy2(src, dst)
                print(f"[Logs] ✅ Synced run_log.csv to {dst}")
            else:
                print(f"[Logs] ⚠️ run_log.csv not found at {src}")
        else:
            sync_model_category(category, src, COMFYUI_MODEL_BASE)

    print("✅ All model categories synced.")
    print(f"🏁 Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
