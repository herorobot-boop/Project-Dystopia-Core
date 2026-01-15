import os
import json
from scripts.mapper import ChronosMapperV3_2

def reapply_lora_to_scene(scene_path, lora_name, strength=0.7):
    with open(scene_path, "r") as f:
        data = json.load(f)

    payload = data["payload"]
    payload["visual_sens"]["lora"] = [f"{lora_name}:{strength}"]

    # 再構築
    mapper = ChronosMapperV3_2(
        template_path="/workspace/templates/chronos_v3_uni3c.json",
        output_dir="/workspace/Phase_V/RunPayloads"
    )

    pose_path = f"/workspace/Phase_V/Inputs/pose_{payload['core_struct']['type_a']}.png"
    json_path = mapper.build_payload(build_prompt({"payload": payload}), pose_path)

    print(f"✅ LoRA再適用完了 → {json_path}")
    return json_path
