import json
import os
from pathlib import Path

def interpolate_value(v1, v2, t):
    return v1 * (1 - t) + v2 * t

def interpolate_tag(tag1, tag2, t):
    return tag1 if t < 0.5 else tag2

def morph_hk9_struct(scene1_path, scene2_path, output_dir, steps=24):
    """
    [HERO's Architecture: ペイロード内の階層構造（core, visual, anomaly, type_f）を維持]
    """
    try:
        with open(scene1_path, 'r', encoding='utf-8') as f:
            s1 = json.load(f)['payload']
        with open(scene2_path, 'r', encoding='utf-8') as f:
            s2 = json.load(f)['payload']
    except Exception as e:
        print(f"[-] Morph Load Error: {e}")
        return

    os.makedirs(output_dir, exist_ok=True)

    for i in range(steps):
        t = i / (steps - 1)
        # HERO's structural mapping
        morph = {
            "payload": {
                "core_struct": {
                    "type_a": interpolate_tag(s1["core_struct"]["type_a"], s2["core_struct"]["type_a"], t),
                    "fov": interpolate_tag(s1["core_struct"]["fov"], s2["core_struct"]["fov"], t)
                },
                "visual_sens": {
                    "type_b": interpolate_tag(s1["visual_sens"]["type_b"], s2["visual_sens"]["type_b"], t),
                    "type_c": interpolate_tag(s1["visual_sens"]["type_c"], s2["visual_sens"]["type_c"], t),
                    "lora": s1["visual_sens"].get("lora") 
                },
                "env_override": {
                    "type_d": interpolate_tag(s1["env_override"]["type_d"], s2["env_override"]["type_d"], t)
                },
                "anomaly": {
                    "type_e": interpolate_tag(s1["anomaly"]["type_e"], s2["anomaly"]["type_e"], t)
                },
                "type_f": {
                    "motion_type": interpolate_tag(s1["type_f"]["motion_type"], s2["type_f"]["motion_type"], t),
                    "intensity": round(interpolate_value(s1["type_f"]["intensity"], s2["type_f"]["intensity"], t), 3),
                    "rhythm": interpolate_tag(s1["type_f"]["rhythm"], s2["type_f"]["rhythm"], t),
                    "deformation": interpolate_tag(s1["type_f"]["deformation"], s2["type_f"]["deformation"], t)
                }
            }
        }

        out_path = os.path.join(output_dir, f"morph_{i:03}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(morph, f, indent=2, ensure_ascii=False)

    print(f"✅ {steps}段階の変容構造JSONを出力しました → {output_dir}")
