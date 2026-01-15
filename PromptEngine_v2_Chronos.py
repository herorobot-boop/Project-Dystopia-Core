import json
from datetime import datetime

def build_prompt(payload):
    core = payload["core_struct"]
    visual = payload["visual_sens"]
    env = payload["env_override"]
    anomaly = payload["anomaly"]
    motion = payload.get("type_f", {})

    # Positive prompt
    positive = ", ".join([
        visual["type_b"],
        visual["type_c"],
        env["type_d"],
        core["type_a"],
        core["fov"],
        "cinematic lighting",
        "high detail"
    ])

    # Negative prompt
    negative = "deformed, blurry, lowres, watermark, duplicate"

    # LoRA
    lora_list = visual.get("lora", [])

    # Motion
    motion_type = motion.get("motion_type", "StaticPulse")
    intensity = motion.get("intensity", 0.5)
    rhythm = motion.get("rhythm", "steady")
    deformation = motion.get("deformation", "None")

    # Pose image path (構図)
    pose_image_path = f"/workspace/Phase_V/Inputs/pose_{core['type_a']}.png"

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

# 使用例
if __name__ == "__main__":
    with open("scene_01.json", "r") as f:
        data = json.load(f)
    result = build_prompt(data["payload"])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    with open(f"RunPayloads/prompt_{timestamp}.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Prompt構築完了 → prompt_{timestamp}.json")
