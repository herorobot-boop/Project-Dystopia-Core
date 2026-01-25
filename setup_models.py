import os
import shutil
from datetime import datetime
from pathlib import Path

# --- 神経接続：プロジェクトルートの特定 ---
BASE_DIR = Path(__file__).resolve().parent

# === 設定：ソース（Google Drive側）の定義 ===
# あなたの既存のパス構造を維持
GDRIVE_BASE = Path("gdrive/MyDrive/Project-Dystopia")
MODEL_CATEGORIES = {
    "checkpoints": GDRIVE_BASE / "models/Checkpoints",
    "loras": GDRIVE_BASE / "models/LoRA",
    "vae": GDRIVE_BASE / "models/VAE",
    "clip": GDRIVE_BASE / "models/Clip",
    "unet": GDRIVE_BASE / "models/Unet",
    "embeddings": GDRIVE_BASE / "models/Embeddings",
    "adetailer": GDRIVE_BASE / "models/ADetailer",
    "RunPayloads": GDRIVE_BASE / "RunPayloads",
    "Outputs": GDRIVE_BASE / "outputs",
    "Logs": GDRIVE_BASE / "run_log.csv",
    "DraftLLM": GDRIVE_BASE / "LLM/Draft"
}

# === 設定：デスティネーション（RunPodローカル側）の定義 ===
# プロジェクトの新構造に合わせて再定義
LOCAL_MODEL_BASE = Path("/workspace/models") # ComfyUIが参照する実体パス
LOCAL_ASSET_DIR = BASE_DIR / "config/assets"
LOCAL_PAYLOAD_DIR = BASE_DIR / "outputs/payload_logs"
LOCAL_OUTPUT_DIR = BASE_DIR / "outputs/images"
DRAFT_LLM_PATH = Path("/workspace/llm_draft")

def sync_resource(category, src_path, dst_path, is_file=False):
    """
    [HERO's Sync Logic: 存在しないファイルのみを高速にコピーする]
    """
    os.makedirs(dst_path if not is_file else dst_path.parent, exist_ok=True)

    if not src_path.exists():
        print(f"[{category}] ⚠️ Source not found: {src_path}")
        return

    if is_file:
        if not dst_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"[{category}] ✅ Synced file: {dst_path.name}")
        return

    copied = 0
    for filename in os.listdir(src_path):
        src_file = src_path / filename
        dst_file = dst_path / filename
        if not dst_file.exists():
            if src_file.is_file():
                shutil.copy2(src_file, dst_file)
                copied += 1
    
    if copied > 0:
        print(f"[{category}] ✅ Synced {copied} new files to {dst_path}")
    else:
        print(f"[{category}] 🟢 Already up-to-date.")

def main():
    print(f"🧠 [H-K9 setup_models.py] Starting specialized resource sync...")
    print(f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for category, src in MODEL_CATEGORIES.items():
        # 1. ログファイルの同期
        if category == "Logs":
            dst = BASE_DIR / "run_log.csv"
            sync_resource(category, src, dst, is_file=True)

        # 2. 思想ペイロード・生成物の同期
        elif category == "RunPayloads":
            sync_resource(category, src, LOCAL_PAYLOAD_DIR)
        elif category == "Outputs":
            sync_resource(category, src, LOCAL_OUTPUT_DIR)

        # 3. LLMドラフトモデルの同期
        elif category == "DraftLLM":
            sync_resource(category, src, DRAFT_LLM_PATH)

        # 4. ComfyUIモデル資産の同期（実体パスへ）
        else:
            # カテゴリ名を小文字に統一してパスを構築
            dst = LOCAL_MODEL_BASE / category.lower()
            sync_resource(category, src, dst)

    print("\n✅ All H-K9 resource categories synced to localized environment.")
    print(f"🏁 Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
