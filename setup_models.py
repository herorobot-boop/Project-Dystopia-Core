import os
import shutil

# GDrive上のモデル格納パス
MODEL_PATHS = {
    "checkpoints": "/workspace/gdrive/MyDrive/AI_Models/Checkpoints/",
    "loras": "/workspace/gdrive/MyDrive/AI_Models/Loras/",
    "vae": "/workspace/gdrive/MyDrive/AI_Models/vae/",
    "clip": "/workspace/gdrive/MyDrive/AI_Models/clip/",
    "unet": "/workspace/gdrive/MyDrive/AI_Models/unet/",
    "embeddings": "/workspace/gdrive/MyDrive/AI_Models/embeddings/",
    "adetailer": "/workspace/gdrive/MyDrive/AI_Models/Tools_ADetailer/"
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

def sync_models():
    for key, src in MODEL_PATHS.items():
        dst = os.path.join(COMFY_PATH, TARGETS[key])
        os.makedirs(dst, exist_ok=True)
        for root, _, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst, file)
                if not os.path.exists(dst_file):
                    print(f"🔄 Syncing: {file}")
                    shutil.copy2(src_file, dst_file)

if __name__ == "__main__":
    sync_models()
    print("✅ モデル同期完了")
