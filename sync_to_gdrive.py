import os
import shutil
from datetime import datetime
from pathlib import Path

# --- 神経接続：プロジェクトルートの特定 ---
BASE_DIR = Path(__file__).resolve().parent

# === 設定：ソース（RunPodローカル側） ===
# 生成された画像、動画、および思想ログの保存先
LOCAL_OUTPUT_DIR = BASE_DIR / "outputs"
LOCAL_LOG_FILE = BASE_DIR / "run_log.csv"

# === 設定：デスティネーション（Google Drive側） ===
# Gdriveがマウントされているパスを指定
GDRIVE_BASE = Path("gdrive/MyDrive/Project-Dystopia")
GDRIVE_OUTPUT_DIR = GDRIVE_BASE / "outputs"
GDRIVE_LOG_FILE = GDRIVE_BASE / "run_log.csv"

def sync_back_to_gdrive():
    """
    [H-K9 Logistics: RunPod上の成果をGoogle Driveへ安全に搬出する]
    差分のみを抽出し、Gdriveの200GB領土へアーカイブします。
    """
    print(f"📦 [H-K9 sync_to_gdrive] Exporting specialized results to Google Drive...")
    print(f"⏱️ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 成果物フォルダの同期
    if LOCAL_OUTPUT_DIR.exists():
        os.makedirs(GDRIVE_OUTPUT_DIR, exist_ok=True)
        copied_files = 0
        
        # サブフォルダ（images, payload_logs, evolved_thoughtsなど）を再帰的に巡回
        for root, dirs, files in os.walk(LOCAL_OUTPUT_DIR):
            for file in files:
                src_file = Path(root) / file
                # Gdrive側の相対パスを計算して、新構造を維持
                rel_path = src_file.relative_to(LOCAL_OUTPUT_DIR)
                dst_file = GDRIVE_OUTPUT_DIR / rel_path
                
                # 同期先ディレクトリの自動生成
                os.makedirs(dst_file.parent, exist_ok=True)
                
                # 差分同期：存在しない、あるいはサイズが異なる場合にコピー
                if not dst_file.exists() or src_file.stat().st_size != dst_file.stat().st_size:
                    shutil.copy2(src_file, dst_file)
                    copied_files += 1
        
        print(f"✅ Outputs: {copied_files} new files exported to Gdrive.")
    else:
        print(f"⚠️ Warning: Local output directory not found: {LOCAL_OUTPUT_DIR}")

    # 2. 実行ログCSVの同期（最新の進捗を上書き）
    if LOCAL_LOG_FILE.exists():
        try:
            shutil.copy2(LOCAL_LOG_FILE, GDRIVE_LOG_FILE)
            print(f"✅ Log: '{LOCAL_LOG_FILE.name}' has been updated on Gdrive.")
        except Exception as e:
            print(f"[-] Log Sync Error: {e}")

    print("\n🏁 Gdrive Extraction Completed. Instance can be safely terminated.")
    print(f"⏱️ Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    sync_back_to_gdrive()
