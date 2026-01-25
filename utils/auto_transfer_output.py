import os
import shutil
from datetime import datetime
from pathlib import Path

# --- 神経接続：プロジェクトルートの特定 ---
BASE_DIR = Path(__file__).resolve().parents[1]

# === 設定：新構造の outputs ディレクトリへ適合 ===
# RunPod内の生成先（ComfyUIの出力先と合わせる）
LOCAL_OUTPUT_DIR = BASE_DIR / "outputs/images"
# GDrive（マウントされている場合）の同期先
GDRIVE_OUTPUT_DIR = Path("/content/drive/MyDrive/H-K9_Assets/Project-Dystopia-Core/Output")
DEFAULT_TAG = "UnknownMotion_UnknownLoRA"

def transfer_outputs(motion_tag=None, lora_tag=None):
    """
    生成された成果物を整理し、GDrive（存在すれば）へ転送する。
    [HERO's Management Logic Preserved: タイムスタンプ命名規則を維持]
    """
    # 転送先ディレクトリの確保
    if not GDRIVE_OUTPUT_DIR.parent.exists():
        print(f"[-] GDrive not mounted. Skipping cloud transfer.")
        return

    os.makedirs(GDRIVE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

    # 転送対象の拡張子
    valid_extensions = (".mp4", ".png", ".jpg", ".webp")

    for fname in os.listdir(LOCAL_OUTPUT_DIR):
        if fname.lower().endswith(valid_extensions):
            src = LOCAL_OUTPUT_DIR / fname

            # タグが指定されていない場合のデフォルト
            m_tag = motion_tag if motion_tag else "Active"
            l_tag = lora_tag if lora_tag else "SDXL"

            # HERO's Naming Rule: timestamp_motion_lora
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            extension = Path(fname).suffix
            new_name = f"{timestamp}_{m_tag}_{l_tag}{extension}"
            
            dst = GDRIVE_OUTPUT_DIR / new_name

            try:
                # すでに転送済みのファイルを二重転送しないためのガード（任意）
                shutil.copy2(src, dst)
                print(f"✅ 転送完了: {new_name} -> GDrive")
            except Exception as e:
                print(f"[-] Transfer Error ({fname}): {e}")

if __name__ == "__main__":
    # テスト実行
    print(f"[*] Checking outputs in: {LOCAL_OUTPUT_DIR}")
    transfer_outputs()
