import json
import shutil
import time
from pathlib import Path

# --- 設定 ---
COMFY_OUTPUT_DIR = Path("/workspace/ComfyUI/output")
PAYLOAD_LOG_DIR = Path("/workspace/Project-Dystopia/outputs/payload_logs")
IMAGE_ARCHIVE_DIR = Path("/workspace/Project-Dystopia/outputs/images")
THOUGHT_LOG_PATH = Path("/workspace/Project-Dystopia/outputs/thought_log.jsonl")

IMAGE_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def match_and_log():
    """
    ComfyUIの出力画像と思想ログを照合し、アーカイブする。
    """
    processed_count = 0
    # 既存のログを読み込んで、二重登録を防止（将来的な拡張用）
    existing_ids = set()
    if THOUGHT_LOG_PATH.exists():
        with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    existing_ids.add(json.loads(line)["prompt_id"])
                except: continue

    # payload_logs 内の全てのJSONをチェック
    for payload_file in PAYLOAD_LOG_DIR.glob("*.json"):
        prompt_id = payload_file.stem
        if prompt_id in existing_ids:
            continue

        # ComfyUIの出力ファイルを探す（ファイル名にprompt_idが含まれているものを検索）
        # ComfyUI側で "filename_prefix": "Dystopia_%prompt_id%" 等の設定を推奨
        found_img = None
        for img_path in COMFY_OUTPUT_DIR.glob(f"*{prompt_id}*.png"):
            found_img = img_path
            break
        
        if not found_img:
            continue

        # アーカイブ先へコピー
        archived_img_path = IMAGE_ARCHIVE_DIR / f"{prompt_id}.png"
        shutil.copy(found_img, archived_img_path)

        # 思想データの読み込み
        with open(payload_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # prompt_to_comfy.py の構造に合わせて取得
            thought = data.get("thought", data) # 構造の差異を吸収

        # ログエントリの作成
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "prompt_id": prompt_id,
            "scene": thought.get("scene_context", "unknown"),
            "positive": data["params"]["positive_prompt"] if "params" in data else "",
            "loras": data["params"]["loras"] if "params" in data else [],
            "seed": data["params"]["seed"] if "params" in data else None,
            "image_path": str(archived_img_path)
        }

        # JSONLに追記
        with open(THOUGHT_LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        print(f"✅ Linked & Archived: {prompt_id}")
        processed_count += 1

    print(f"\n✨ Processed {processed_count} new thoughts.")

if __name__ == "__main__":
    match_and_log()
