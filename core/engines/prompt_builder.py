import json
import sys
from pathlib import Path

# --- 神経接続：プロジェクトルートの動的特定 ---
BASE_DIR = Path(__file__).resolve().parents[2]

# --- 同階層のエンジンを読み込めるように設定 ---
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

def apply_physics_weight(text: str) -> str:
    """
    特定の物理干渉キーワードを検知し、強制的に強調ウェイトを付与する。
    """
    critical_keywords = [
        "indentation", "flesh overlap", "squish", "clinging", 
        "permeation", "backflow", "deformation", "skin redness",
        "resource accumulation", "tightness"
    ]
    
    words = text.split(", ")
    weighted_words = []
    for word in words:
        if any(ck in word.lower() for ck in critical_keywords):
            # 物理キーワードには1.3のウェイトを強制
            weighted_words.append(f"({word}:1.3)")
        else:
            weighted_words.append(word)
    return ", ".join(weighted_words)

def build_prompt(thought_json: dict, negative: bool = False) -> str:
    """
    [H-K9 Architecture: 物理強調ロジックを組み込んだプロンプト構築]
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
            # 有料版では「清潔感」や「美化」をネガティブに叩き込む
            base_negatives += ["perfect symmetry", "studio lighting", "airbrushed skin", "makeup", "clean"]
        
        return ", ".join(base_negatives)

    # --- ポジティブプロンプト構築 ---
    
    # LoRAタグ
    lora_tags = [f"<lora:{l['name']}:{l['weight']}>" for l in thought_json.get("lora_settings", [])]

    # Identity（人物記述）
    identity_tags = thought_json.get("identity_tag", "1girl")

    # 構成要素の取得と物理強調の適用
    vc = thought_json.get("visual_config", {})
    view = vc.get("view", "").replace("_", " ")
    lighting = vc.get("lighting", "").replace("_", " ")
    focus = vc.get("focus_strategy", "").replace("_", " ")
    scene = apply_physics_weight(thought_json.get("scene_context", ""))

    # 質感・干渉
    fabric_logic = thought_json.get("fabric_logic", {})
    fabric = apply_physics_weight(fabric_logic.get("material_interaction", "").replace("_", " "))
    action = fabric_logic.get("action_state", "").replace("_", " ")
    
    # 生理反応 (Paidのみ強調)
    physiology = thought_json.get("physiology_detail", "").replace("_", " ")
    if physiology:
        physiology = f"({physiology}:1.4)" # 生理反応は最優先

    # リアリズム・光学
    realism_tags = [t.replace("_", " ") for t in thought_json.get("realism_tags", [])]
    overrides = thought_json.get("global_overrides", {})
    optical = overrides.get("optical", "").replace("_", " ")
    physics = apply_physics_weight(overrides.get("physics", "").replace("_", " "))

    # --- 最終結合 ---
    prompt_parts = [
        *lora_tags,
        "masterpiece, best quality, photographic, sharp focus, raw photo",
        scene,
        identity_tags,
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
    try:
        from thought_generator import generate_thought
        # テスト実行
        thought = generate_thought("tight lora test with resource", context_type="paid")
        print("\n🧠 H-K9 Physics-Boosted Prompt:\n", build_prompt(thought))
    except Exception as e:
        print(f"[-] Error: {e}")
