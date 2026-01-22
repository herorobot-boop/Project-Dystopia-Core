import json
from pathlib import Path

def build_prompt(thought_json: dict) -> str:
    """
    思想JSONをもとに、因果関係と優先順位を考慮して画像生成用のプロンプトを構築する。
    """
    
    # --- 1. Identity & Character ---
    identity = thought_json["global_overrides"].get("identity", "")
    identity_tags = identity.replace("identity_anchor_active:", "").replace("_", " ").strip()

    # --- 2. Composition & Context (最優先) ---
    view = thought_json["visual_config"].get("view", "").replace("_", " ")
    lighting = thought_json["visual_config"].get("lighting", "").replace("_", " ")
    focus = thought_json["visual_config"].get("focus_strategy", "").replace("_", " ")
    scene = thought_json.get("scene_context", "")

    # --- 3. Interaction & Action (因果律) ---
    fabric = thought_json.get("fabric_logic", {}).get("material_interaction", "").replace("_", " ")
    action = thought_json.get("fabric_logic", {}).get("action_state", "").replace("_", " ")

    # --- 4. Deep Physiological Details (Paid/Teaser用) ---
    physiology = thought_json.get("physiology_detail", "").replace("_", " ")
    # 重要度が高いため、少し強調をかける
    if physiology:
        physiology = f"({physiology}:1.2)"

    # --- 5. Realism Tags (知識ベース) ---
    realism_tags = [t.replace("_", " ") for t in thought_json.get("realism_tags", [])]
    
    # --- 6. Optical & Physical Noise (最後に配置) ---
    optical = thought_json["global_overrides"].get("optical", "").replace("_", " ")
    physics = thought_json["global_overrides"].get("physics", "").replace("_", " ")

    # --- 7. プロンプトの組み立て (因果関係順) ---
    # 視覚の入り口（構図・光） -> 被写体の状態（服・動作） -> 生命感（生理反応） -> 仕上げ（ノイズ）
    prompt_parts = [
        f"masterpiece, best quality, ultra-detailed", # 基本品質
        f"{scene}",
        f"{view}, {lighting}, {focus}",
        f"{identity_tags}",
        f"{fabric}, {action}",
        f"{physiology}",
        ", ".join(realism_tags),
        f"{optical}",
        f"{physics}"
    ]

    # 空要素を除外し、クリーニング
    final_prompt = ", ".join([p for p in prompt_parts if p and p.strip()])
    
    # アンダースコアをスペースに統一し、重複するスペースを削除
    final_prompt = final_prompt.replace("_", " ")
    
    return final_prompt.strip()

# テスト用
if __name__ == "__main__":
    from thought_generator import generate_thought

    # テスト思想生成 (Paid文脈)
    thought = generate_thought("夕暮れの誰もいない体育館", context_type="paid", variation_id=7)

    # プロンプト構築
    prompt = build_prompt(thought)
    print("🧠 Integrated Prompt Output:\n")
    print(prompt)
