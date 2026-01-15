from phase_v_reapply import execute_hk9_command
from extract_frames import extract_frames
from auto_tag_refiner import refine_folder
import os

def run_cycle(scene_json, lora_name, strength=0.7):
    # 1. 動画生成
    execute_hk9_command(scene_json, mode="VIDEO")

    # 2. フレーム抽出
    extract_frames("refined_output.mp4", "./dataset/train", interval=6)

    # 3. タグ生成（別途BLIPで実行）
    # annotate_folder("./dataset/train") ← 既出スクリプト

    # 4. タグ補正
    refine_folder("./dataset/train")

    # 5. 再学習
    os.system("accelerate launch train_network.py --config_file lora_trainer_config.json")

    print("✅ Virtual Resource Cycle 完了")
