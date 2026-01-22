import json
import datetime
import random
from pathlib import Path

# パスの設定
BASE_DIR = Path("/workspace/Project-Dystopia")
TEMPLATE_PATH = BASE_DIR / "config/thought_template_master.json"

def load_thought_template(path=TEMPLATE_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Template not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_thought(scene_context: str, context_type: str = "free", variation_id: int = 0, char_lora: str = None):
    """
    人物固定なしのランダム生成、または特定キャラLoRAの受肉を選択可能な思想生成エンジン。
    """
    template = load_thought_template()
    
    if context_type not in template["context_matrix"]:
        context_type = "free"
    
    ctx = template["context_matrix"][context_type]
    genetics = template["realism_genetics"]
    
    # 構図の判定
    view_str = ctx["view"].lower()
    
    # --- LoRA & Identity ロジック ---
    lora_settings = []
    
    if char_lora:
        # 【特定キャラ受肉モード】指定があればウェイト計算して適用
        weight = 0.85 if "close-up" in view_str else 0.75
        lora_settings.append({"name": char_lora, "weight": weight})
        # IdentityタグはLoRAに合わせて簡潔に
        identity_tag = "1girl, unique individual"
    else:
        # 【流動的Identityモード】固定LoRAなし。タグで人物像を揺らす
        # ここを書き換えるだけで、生成される女の子の属性が変わる
        identity_tag = random.choice([
            "1girl, japanese school girl, messy hair",
            "1girl, shy office lady, spectacles",
            "1girl, young woman, casual summer wear",
            "1girl, expressive student, pigtails"
        ])

    # --- シーン特化LoRAの自動適用（Gdrive資産の活用例） ---
    # シーンやアングルに応じて、アセットリストにあるLoRAを自動で混ぜる
    if "pov" in view_str or context_type == "paid":
        lora_settings.append({"name": "Pov_xl_v1.5", "weight": 0.4})
    
    if "phone" in scene_context or "電話" in scene_context:
        lora_settings.append({"name": "Japanese_Public_Phone_SDXL", "weight": 0.8})

    # 基本構造の構築
    base = {
        "project": template["project"],
        "timestamp": datetime.datetime.now().isoformat(),
        "scene_context": scene_context,
        "context_type": context_type,
        "variation_id": variation_id,
        "identity_tag": identity_tag, # 人物の記述
        "global_overrides": template["global_overrides"],
        "lora_settings": lora_settings,
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

    # 因果律指示の構築
    base["prompt_construction_logic"] = {
        "causality": f"The character '{identity_tag}' is placed in '{scene_context}'.",
        "hierarchy": ["1. Occlusion/View", "2. Identity/Tags", "3. Physiology", "4. Noise"],
        "interaction": f"{genetics['fabric_logic']['material_interaction']} during {genetics['fabric_logic']['action_state']}"
    }

    return base

if __name__ == "__main__":
    # テスト：キャラ固定なしで生成
    thought = generate_thought("夜の公衆電話、雨", context_type="paid")
    print(json.dumps(thought, indent=2, ensure_ascii=False))
