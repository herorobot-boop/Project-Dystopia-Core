import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# --- パス設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
LOG_PATH = BASE_PATH / "outputs/thought_log.jsonl"
IMAGE_DIR = BASE_PATH / "outputs/images"
# Kohya_ssの仕様に合わせたディレクトリ構造 (100_concept)
TRAIN_CONCEPT_DIR = BASE_PATH / "training_data/100_dystopia"
LORA_OUTPUT_DIR = BASE_PATH / "lora_outputs"
LORA_ASSET_CSV = BASE_PATH / "config/lora_assets.csv"
KOHYA_PATH = Path("/workspace/sd-scripts") # RunPodでの標準的なkohyaパス

def prepare_training_data(min_score=8.5, limit=50):
    """高スコア画像を抽出し、キャプションファイルを生成"""
    if not LOG_PATH.exists(): return 0

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        logs = [json.loads(line) for line in f if line.strip()]
    
    selected = [e for e in logs if e.get("score", 0) >= min_score]
    selected = sorted(selected, key=lambda x: x["score"], reverse=True)[:limit]

    # フォルダのクリーンアップと再作成
    if TRAIN_CONCEPT_DIR.exists(): shutil.rmtree(TRAIN_CONCEPT_DIR)
    TRAIN_CONCEPT_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for entry in selected:
        pid = entry["prompt_id"]
        img_src = IMAGE_DIR / f"{pid}.png"
        if img_src.exists():
            # 画像のコピー
            shutil.copy(img_src, TRAIN_CONCEPT_DIR / f"{pid}.png")
            # キャプションの生成 (思想文をそのままタグとして利用)
            caption_text = entry.get("scene", "").replace("、", ", ")
            with open(TRAIN_CONCEPT_DIR / f"{pid}.txt", "w", encoding="utf-8") as f:
                f.write(caption_text)
            count += 1
    return count

def run_kohya_training(lora_name):
    """A100のパワーを解放し、実際に学習を行う"""
    LORA_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 実行コマンド (最小限かつ強力な設定)
    cmd = [
        "python", str(KOHYA_PATH / "train_network.py"),
        "--pretrained_model_name_or_path=runwayml/stable-diffusion-v1-5", # またはSDXL
        f"--train_data_dir={TRAIN_CONCEPT_DIR.parent}",
        f"--output_dir={LORA_OUTPUT_DIR}",
        f"--output_name={lora_name}",
        "--resolution=512,512",
        "--train_batch_size=4",
        "--max_train_epochs=10",
        "--learning_rate=1e-4",
        "--network_module=networks.lora",
        "--mixed_precision=fp16",
        "--save_model_as=safetensors",
        "--xformers"
    ]
    
    print(f"🔥 Starting LoRA Training: {lora_name}")
    result = subprocess.run(cmd)
    return result.returncode == 0

def register_to_assets(lora_name):
    """新しく産まれたLoRAを即戦力として登録"""
    file_name = f"{lora_name}.safetensors"
    if not LORA_ASSET_CSV.exists():
        with open(LORA_ASSET_CSV, "w", encoding="utf-8") as f:
            f.write("name,file\n")
    
    with open(LORA_ASSET_CSV, "a", encoding="utf-8") as f:
        f.write(f"{lora_name},{file_name}\n")
    print(f"✅ Registered {lora_name} to assets.")

if __name__ == "__main__":
    # 1. 教師データの準備
    img_count = prepare_training_data()
    if img_count < 5:
        print(f"⚠️ 素材不足 (現在 {img_count}枚)。学習には最低5〜10枚の高スコア画像が必要です。")
    else:
        # 2. 学習実行
        timestamp = datetime.now().strftime("%m%d_%H%M")
        new_lora_name = f"dystopia_evo_{timestamp}"
        if run_kohya_training(new_lora_name):
            # 3. 資産登録
            register_to_assets(new_lora_name)
