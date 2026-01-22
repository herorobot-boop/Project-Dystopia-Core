import json
from pathlib import Path

def build_prompt(thought_json: dict, negative: bool = False) -> str:
    """
    思想JSONから、LoRAタグ付きポジティブプロンプト、
    または文脈に応じたネガティブプロンプトを構築する。
    """
    context = thought_json.get("context_type", "free")

    # --- 1. ネガティブプロンプト構築 ---
    if negative:
        base_negatives = [
            "worst quality", "low quality", "normal quality", "jpeg artifacts",
            "blurry", "extra fingers", "missing fingers", "bad anatomy",
            "bad hands", "text", "error", "cropped", "signature", "watermark",
            "username", "artist name", "fused fingers", "long neck", "bad feet",
            "oversaturated", "overexposed", "flat lighting"
        ]

        if context == "free":
            # SNSセーフティ(SFW)を強化
            base_negatives += [
                "nsfw", "nude", "cleavage", "underwear", "suggestive", 
                "extreme expression", "unusual lighting", "nipples", "pussy"
            ]
        elif context == "paid":
            # AI的完璧さを排除し、実写(Non-Censored/UGC)を強制
            base_negatives += [
                "perfect symmetry", "studio lighting", "airbrushed skin", 
                "plastic skin", "makeup", "caricature", "doll-like"
            ]

        return ", ".join(base_negatives)

    # --- 2. ポジティブプロンプト構築 ---
    
    # LoRAタグ生成
    lora_tags = []
    for lora in thought_json.get("lora_settings", []):
        name = lora.get("name", "").strip()
        weight = lora.get("weight", 1.0)
        if name:
            lora_tags.append(f"<lora:{name}:{weight}>")

    # キャラクター・不変要素
    identity = thought_json["global_overrides"].get("identity", "")
    identity_tags = identity.replace("identity_anchor_active:", "").replace("_", " ").strip()

    # 構図・照明・シーン
    view = thought_json["visual_config"].get("view", "").replace("_", " ")
    lighting = thought_json["visual_config"].get("lighting", "").replace("_", " ")
    focus = thought_json["visual_config"].get("focus_strategy", "").replace("_", " ")
    scene = thought_json.get("scene_context", "")

    # 物理干渉
    fabric = thought_json.get("fabric_logic", {}).get("material_interaction", "").replace("_", " ")
    action = thought_json.get("fabric_logic", {}).get("action_state", "").replace("_", " ")

    # 生理反応 (重み付け)
    physiology = thought_json.get("physiology_detail", "").replace("_", " ")
    if physiology:
        physiology = f"({physiology}:1.2)"

    # 質感・ノイズ
    realism_tags = [t.replace("_", " ") for t in thought_json.get("realism_tags", [])]
    optical = thought_json["global_overrides"].get("optical", "").replace("_", " ")
    physics = thought_json["global_overrides"].get("physics", "").replace("_", " ")

    # --- 最終構築（優先順位：LoRA > 品質 > シーン > 構図 > 物理 > 生理 > ノイズ） ---
    prompt_parts = [
        *lora_tags,
        "masterpiece, best quality, ultra-detailed",
        scene,
        f"{view}, {lighting}, {focus}",
        identity_tags,
        f"{fabric}, {action}",
        physiology,
        ", ".join(realism_tags),
        optical,
        physics
    ]

    final_prompt = ", ".join([p for p in prompt_parts if p and p.strip()])
    final_prompt = final_prompt.replace("_", " ")

    return final_prompt.strip()

if __name__ == "__main__":
    from thought_generator import generate_thought

    # 実働テスト
    target_scene = "雨の降る深夜の駅のホーム"
    
    # PAIDの生成
    paid_thought = generate_thought(target_scene, context_type="paid")
    print("💎 [PAID] Positive:\n", build_prompt(paid_thought))
    print("\n🚫 [PAID] Negative:\n", build_prompt(paid_thought, negative=True))
