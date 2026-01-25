import json
import os

def interpolate_value(v1, v2, t):
    return v1 * (1 - t) + v2 * t

def interpolate_tag(tag1, tag2, t):
    return tag1 if t < 0.5 else tag2

def morph_hk9_struct(scene1_path, scene2_path, output_dir, steps=24):
    with open(scene1_path, 'r') as f:
        s1 = json.load(f)['payload']
    with open(scene2_path, 'r') as f:
        s2 = json.load(f)['payload']

    os.makedirs(output_dir, exist_ok=True)

    for i in range(steps):
        t = i / (steps - 1)
        morph = {
            "payload": {
                "core_struct": {
                    "type_a": interpolate_tag(s1["core_struct"]["type_a"], s2["core_struct"]["type_a"], t),
                    "fov": interpolate_tag(s1["core_struct"]["fov"], s2["core_struct"]["fov"], t)
                },
                "visual_sens": {
                    "type_b": interpolate_tag(s1["visual_sens"]["type_b"], s2["visual_sens"]["type_b"], t),
                    "type_c": interpolate_tag(s1["visual_sens"]["type_c"], s2["visual_sens"]["type_c"], t),
                    "lora": s1["visual_sens"]["lora"]  # 固定（必要に応じて補間可能）
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
        with open(out_path, 'w') as f:
            json.dump(morph, f, indent=2)

    print(f"✅ {steps}構造JSONを出力しました → {output_dir}")
