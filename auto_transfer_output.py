import os
import shutil
from datetime import datetime

# === 設定 ===
LOCAL_OUTPUT_DIR = "/workspace/Phase_V/Output"
GDRIVE_OUTPUT_DIR = "/content/drive/MyDrive/H-K9_Assets/Phase_V/Output"
DEFAULT_TAG = "UnknownMotion_UnknownLoRA"

def transfer_outputs():
    os.makedirs(GDRIVE_OUTPUT_DIR, exist_ok=True)

    for fname in os.listdir(LOCAL_OUTPUT_DIR):
        if fname.endswith(".mp4") and fname.startswith("refined_output"):
            src = os.path.join(LOCAL_OUTPUT_DIR, fname)

            # タグ抽出（仮：ファイル名 or メタデータから取得）
            motion_tag = "AxialIteration"  # TODO: 自動抽出に対応
            lora_tag = "SkinDetail"        # TODO: 自動抽出に対応

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            new_name = f"{timestamp}_{motion_tag}_{lora_tag}.mp4"
            dst = os.path.join(GDRIVE_OUTPUT_DIR, new_name)

            shutil.copy2(src, dst)
            print(f"✅ 転送完了: {new_name}")

# 実行
# transfer_outputs()
