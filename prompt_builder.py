import json
from pathlib import Path

def build_prompt(thought_json: dict, negative: bool = False) -> str:
    """
    思想JSONをもとに、画像生成用のポジティブ/ネガティブプロンプトを構築する。
    Free(SFW)とPaid(NSFW)で出力の質を自動的に切り替える。
    """

    context = thought_json.get("context_type", "free")

    if negative:
        # --- 1. 共通のネガティブ要素（低品質の排除） ---
        base_negatives = [
            "worst quality", "low quality", "normal quality", "jpeg artifacts",
            "blurry", "extra fingers", "missing fingers", "bad anatomy",
            "bad hands", "text", "error", "cropped", "signature", "watermark",
            "username", "artist name", "fused fingers", "long neck", "bad feet",
            "oversaturated", "overexposed", "flat lighting"
        ]

        # --- 2. 文脈別のネガティブ制御 ---
        if context == "free":
            # SNSでの安全性を高め、健全な日常感を守る
            base_negatives += [
                "nsfw", "nude", "cleavage", "underwear", "suggestive", 
                "extreme expression", "unusual lighting", "nipples", "pussy"
            ]
        elif context == "paid":
            # 「AI的な綺麗さ」を排除し、生々しいリアリズムを強制する
            base_negatives += [
                "perfect symmetry", "studio lighting", "airbrushed skin", 
                "plastic skin", "makeup", "caricature", "doll-like"
            ]

        return ", ".join(base_negatives)

    # --- 3. ポジティブプロンプト構築 ---
    # Identity (不変遺伝子)
    identity = thought_json["global_overrides"].get("identity", "")
    identity_tags = identity.replace("identity_anchor_active:", "").replace("_", " ").strip()

    # View & Lighting (構図・照明)
    view = thought_json["visual_config"].get("view", "").replace("_", " ")
    lighting = thought_json["visual_config"].get("lighting", "").replace("_", " ")
    focus = thought_json["visual_config"].get("focus_strategy", "").replace("_", " ")
    scene = thought_json.get("scene_context", "")

    # Physical Interaction (物理・素材干渉)
    fabric = thought_json.get("fabric_logic", {}).get("material_interaction", "").replace("_", " ")
    action = thought_json.get("fabric_logic", {}).get("action_state", "").replace("_", " ")

    # Physiological Reality (生理反応：Paidのみ強く反映)
    physiology = thought_json.get("physiology_detail", "").replace("_", " ")
    if physiology:
        # 生理反応は生々しさの核なので、重み付けを強化
        physiology = f"({physiology}:1.2)"

    # Realism Tags & Optical Defects (質感・ノイズ)
    realism_tags = [t.replace("_", " ") for t in thought_json.get("realism_tags", [])]
    optical = thought_json["global_overrides"].get("optical", "").replace("_", " ")
    physics = thought_json["global_overrides"].get("physics", "").replace("_", " ")

    # --- 4. プロンプトの組み立て (因果関係順) ---
    prompt_parts = [
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

    # 空要素を除外し、最終クリーンアップ
    final_prompt = ", ".join([p for p in prompt_parts if p and p.strip()])
    final_prompt = final_prompt.replace("_", " ")

    return final_prompt.strip()

# --- テスト実行セクション ---
if __name__ == "__main__":
    from thought_generator import generate_thought

    # 1. Paid（有料/ノンセンサード）のテスト
    paid_thought = generate_thought("夕暮れの体育館、放課後", context_type="paid")
    print("💎 [PAID] Positive:\n", build_prompt(paid_thought))
    print("🚫 [PAID] Negative:\n", build_prompt(paid_thought, negative=True))

    print("\n" + "="*50 + "\n")

    # 2. Free（無料/SNS用）のテスト
    free_thought = generate_thought("昼下がりのカフェ", context_type="free")
    print("🕊️ [FREE] Positive:\n", build_prompt(free_thought))
    print("🚫 [FREE] Negative:\n", build_prompt(free_thought, negative=True))
