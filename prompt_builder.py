import json
from pathlib import Path

def build_prompt(thought_json: dict, negative: bool = False) -> str:
    """
    人物固定タグとLoRAタグを統合して、最終的なプロンプトを構築する。
    """
    context = thought_json.get("context_type", "free")

    # --- ネガティブプロンプト構築 ---
    if negative:
        base_negatives = [
            "worst quality", "low quality", "normal quality", "jpeg artifacts",
            "blurry", "bad anatomy", "bad hands", "text", "error", "watermark",
            "username", "artist name", "fused fingers", "plastic skin"
        ]
        if context == "free":
            base_negatives += ["nsfw", "nude", "cleavage", "underwear", "suggestive"]
        elif context == "paid":
            base_negatives += ["perfect symmetry", "studio lighting", "airbrushed skin", "makeup"]
        
        return ", ".join(base_negatives)

    # --- ポジティブプロンプト構築 ---
    
    # LoRAタグ
    lora_tags = [f"<lora:{l['name']}:{l['weight']}>" for l in thought_json.get("lora_settings", [])]

    # Identity（人物記述）
    identity_tags = thought_json.get("identity_tag", "1girl")

    # 構図・照明・シーン
    view = thought_json["visual_config"]["view"].replace("_", " ")
    lighting = thought_json["visual_config"]["lighting"].replace("_", " ")
    focus = thought_json["visual_config"]["focus_strategy"].replace("_", " ")
    scene = thought_json.get("scene_context", "")

    # 質感・干渉
    fabric = thought_json.get("fabric_logic", {}).get("material_interaction", "").replace("_", " ")
    action = thought_json.get("fabric_logic", {}).get("action_state", "").replace("_", " ")
    
    # 生理反応 (Paidのみ)
    physiology = thought_json.get("physiology_detail", "").replace("_", " ")
    if physiology:
        physiology = f"({physiology}:1.2)"

    # リアリズム・光学
    realism_tags = [t.replace("_", " ") for t in thought_json.get("realism_tags", [])]
    optical = thought_json["global_overrides"].get("optical", "").replace("_", " ")
    physics = thought_json["global_overrides"].get("physics", "").replace("_", " ")

    # --- 最終結合（情報の重層構造） ---
    prompt_parts = [
        *lora_tags,
        "masterpiece, best quality, photographic, sharp focus",
        scene,
        identity_tags,  # LoRAがない場合、ここが重要になる
        f"{view}, {lighting}, {focus}",
        f"{fabric}, {action}",
        physiology,
        ", ".join(realism_tags),
        optical,
        physics
    ]

    final_prompt = ", ".join([p for p in prompt_parts if p and p.strip()])
    return final_prompt.replace("_", " ").strip()

if __name__ == "__main__":
    from thought_generator import generate_thought
    
    # テスト出力
    thought = generate_thought("深夜の公園のベンチ", context_type="teaser")
    print("🧠 Integrated Prompt:\n", build_prompt(thought))
