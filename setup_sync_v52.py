import os
import shutil
import re
from datetime import datetime

# === 設定 ===
GDRIVE_LORA_DIR = "/content/drive/MyDrive/H-K9_Assets/loras"
RUNPOD_LORA_DIR = "/workspace/ComfyUI/models/loras"
LOG_PATH = "/workspace/logs/sync_log.txt"

def normalize_filename(filename):
    # バージョン番号や余計な接尾辞を除去して正規化
    base = re.sub(r'_v\d+|_v\d+\.\d+|_V\d+|_V\d+\.\d+', '', filename)
    base = re.sub(r'[\s

\[\]

\(\)]', '', base)  # 空白や記号を除去
    return base

def sync_loras():
    os.makedirs(RUNPOD_LORA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    log_lines = []
    log_lines.append(f"=== H-K9 SYNC START [{datetime.now()}] ===")

    for fname in os.listdir(GDRIVE_LORA_DIR):
        if fname.endswith(".safetensors"):
            src = os.path.join(GDRIVE_LORA_DIR, fname)
            norm_name = normalize_filename(fname)
            dst = os.path.join(RUNPOD_LORA_DIR, norm_name)

            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                log_lines.append(f"[SYNCED] {fname} → {norm_name}")
            else:
                log_lines.append(f"[SKIPPED] {fname} already exists as {norm_name}")

    log_lines.append(f"=== SYNC COMPLETE ===\n")

    with open(LOG_PATH, "a") as log_file:
        log_file.write("\n".join(log_lines) + "\n")

    print(f"✅ LoRA同期完了。ログ: {LOG_PATH}")

# 実行
# sync_loras()
