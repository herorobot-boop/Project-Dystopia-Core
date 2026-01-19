import os
import shutil

# GDrive上のモデル格納パス（読み取り元）
GDRIVE_MODEL_PATHS = {
    "checkpoints": "/workspace/gdrive/MyDrive/AI_Models/Checkpoints/",
    "loras": "/workspace/gdrive/MyDrive/AI_Models/Loras/",
    "vae": "/workspace/gdrive/MyDrive/AI_Models/vae/",
    "clip": "/workspace/gdrive/MyDrive/AI_Models/clip/",
    "unet": "/workspace/gdrive/MyDrive/AI_Models/unet/",
    "embeddings": "/workspace/gdrive/MyDrive/AI_Models/embeddings/",
    "adetailer": "/workspace/gdrive/MyDrive/AI_Models/Tools_ADetailer/"
}

# Volume Disk上のローカル同期先（ComfyUIが参照する）
VOLUME_MODEL_PATHS = {
    "checkpoints": "/workspace/models/Checkpoints/",
    "loras": "/workspace/models/Loras/",
    "vae": "/workspace/models/vae/",
    "clip": "/workspace/models/clip/",
    "unet": "/workspace/models/unet/",
    "embeddings": "/workspace/models/embeddings/",
    "adetailer": "/workspace/models/Tools_ADetailer/"
}

# ComfyUIのモデルディレクトリ
COMFY_PATH = "/workspace/ComfyUI/models"

TARGETS = {
    "checkpoints": "checkpoints",
    "loras": "loras",
    "vae": "vae",
    "clip": "clip",
    "unet": "unet",
    "embeddings": "embeddings",
    "adetailer": "annotator/embeddings"
}

def sync_from_gdrive():
    print("🔄 GDrive → Volume Disk モデル同期開始")
    for key in GDRIVE_MODEL_PATHS:
        src = GDRIVE_MODEL_PATHS[key]
        dst = VOLUME_MODEL_PATHS[key]
        os.makedirs(dst, exist_ok=True)
        for root, _, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst, file)
                if not os.path.exists(dst_file):
                    print(f"📥 コピー中: {file}")
                    shutil.copy2(src_file, dst_file)
    print("✅ GDrive → Volume Disk 同期完了")

def link_to_comfyui():
    print("🔗 Volume Disk → ComfyUI モデルリンク開始")
    for key in VOLUME_MODEL_PATHS:
        src = VOLUME_MODEL_PATHS[key]
        dst = os.path.join(COMFY_PATH, TARGETS[key])
        os.makedirs(dst, exist_ok=True)
        for root, _, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst, file)
                if not os.path.exists(dst_file):
                    print(f"📎 リンク中: {file}")
                    shutil.copy2(src_file, dst_file)
    print("✅ ComfyUI モデル同期完了")

if __name__ == "__main__":
    sync_from_gdrive()
    link_to_comfyui()
