import json
import datetime
from pathlib import Path

# パスの設定
BASE_DIR = Path("/workspace/Project-Dystopia")
TEMPLATE_PATH = BASE_DIR / "config/thought_template_master.json"

def load_thought_template(path=TEMPLATE_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Template not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_thought(scene_context: str, context_type: str = "free", variation_id: int = 0):
    """
    シーンと思想文脈に基づき、LoRAウェイトを自動演算して思想JSONを生成する。
    """
    template = load_thought_template()
    
    if context_type not in template["context_matrix"]:
        context_type = "free"
    
    ctx = template["context_matrix"][context_type]
    genetics = template["realism_genetics"]
    
    # --- 自動LoRAウェイト演算ロジック ---
    # 構図（view）の文字列から「近さ」を判定し、ウェイトを最適化する
    view_str = ctx["view"].lower()
    
    if "extreme" in view_str or "close-up" in view_str:
        # アップは個体の再現性を高めるために強め (0.85)
        calculated_weight = 0.85
    elif "wide" in view_str or "floor" in view_str:
        # 引きは背景や光の干渉を許容し、馴染ませるために弱め (0.7)
        calculated_weight = 0.7
    else:
        # 標準的な距離 (0.8)
        calculated_weight = 0.8

    # 基本構造の構築
    base = {
        "project": template["project"],
        "timestamp": datetime.datetime.now().isoformat(),
        "scene_context": scene_context,
        "context_type": context_type,
        "variation_id": variation_id,
        "global_overrides": template["global_overrides"],
        "lora_settings": [
            {"name": "japanese_girl_v1.1", "weight": calculated_weight}
        ],
        "realism_tags": genetics["tags"],
        "fabric_logic": genetics["fabric_logic"],
        "visual_config": {
            "view": ctx["view"],
            "lighting": ctx["lighting"],
            "focus_strategy": ctx["focus"]
        },
        "meta": ctx["meta"]
    }

    if "physiology" in ctx:
        base["physiology_detail"] = ctx["physiology"]

    # 因果律ロジックの注入
    base["prompt_construction_logic"] = {
        "causality_chain": f"The scene '{scene_context}' requires {calculated_weight} weight for character LoRA based on {view_str}.",
        "hierarchical_priority": ["1. Occlusion", "2. Physiology", "3. Optical_Noise"],
        "interaction_rule": f"Apply {genetics['fabric_logic']['material_interaction']} during {genetics['fabric_logic']['action_state']}."
    }

    return base

if __name__ == "__main__":
    # テスト出力
    thought = generate_thought("放課後の廊下、夕日", context_type="paid")
    print(json.dumps(thought, indent=2, ensure_ascii=False))
