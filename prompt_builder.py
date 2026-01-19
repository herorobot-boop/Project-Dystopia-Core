import json
import os
from datetime import datetime

def build_prompt(payload):
    core = payload.get("core_struct", {})
    visual = payload.get("visual_sens", {})
    env = payload.get("env_override", {})
    anomaly = payload.get("anomaly", {})
    motion = payload.get("type_f", {})

    # Positive prompt
    positive = ", ".join(filter(None, [
        visual.get("type_b"),
        visual.get("type_c"),
        env.get("type_d"),
        core.get("type_a"),
        core.get("fov"),
        "cinematic lighting",
        "high detail"
    ]))

    # Negative prompt
    negative = "deformed, blurry, lowres, watermark, duplicate"

    # LoRA list
    lora_list = visual.get("lora", [])

    # Motion parameters
    motion_type = motion.get("motion_type", "StaticPulse")
    intensity = motion.get("intensity", 0.5)
    rhythm = motion.get("rhythm", "steady")
    deformation = motion.get("deformation", "None")

    # Pose image path
    pose_image_path = f"/workspace/Phase_V/Inputs/pose_{core.get('type_a', 'A00')}.png"

    # Motion bucket ID（仮マッピング）
    motion_bucket_id = {
        "StaticPulse": 0,
        "Axial Iteration": 3,
        "Spiral Drive": 5
    }.get(motion_type, 0)

    return {
        "positive": positive,
        "negative": negative,
        "lora_list": lora_list,
        "pose_image_path": pose_image_path,
        "motion_bucket_id": motion_bucket_id,
        "motion_rhythm": rhythm,
        "motion_intensity": intensity,
        "motion_deformation": deformation
    }

# 実行例
if __name__ == "__main__":
    input_path = "mapped/scene_A01_C01_D02_20260119_180000.json"
    with open(input_path, "r", encoding="utf-8") as f:
        scene_data = json.load(f)

    # payload部分だけ抽出（構造タグに基づく詳細構成が入っている前提）
    payload = scene_data.get("payload", scene_data)  # fallback for raw payloads

    result = build_prompt(payload)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = f"RunPayloads/prompt_{timestamp}.json"
    os.makedirs("RunPayloads", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Prompt構築完了 → {out_path}")
