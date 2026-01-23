import json
import datetime
import random
from pathlib import Path
from lora_selector import select_lora

BASE_DIR = Path("/workspace/Project-Dystopia")
TEMPLATE_PATH = BASE_DIR / "config/thought_template_master.json"

def load_thought_template(path=TEMPLATE_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Template not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_thought(scene_context: str, context_type: str = "free", variation_id: int = 0):
    """
    思想の核を生成し、資産リストから最適な舞台装置(LoRA)を自動召喚する。
    """
    template = load_thought_template()
    
    if context_type not in template["context_matrix"]:
        context_type = "free"
    
    ctx = template["context_matrix"][context_type]
    genetics = template["realism_genetics"]
    view_str = ctx["view"].lower()
    
    # 1. Identity（流動的な人物像の決定）
    identity_tag = random.choice([
        "1girl, japanese school girl, messy hair",
        "1girl, shy office lady, spectacles",
        "1girl, young woman, casual summer wear",
        "1girl, student, uniform"
    ])

    # 2. 自動LoRAセレクターの実行（CSV資産との突合）
    lora_settings = select_lora(scene_context, view_str, context_type)

    # 3. 思想構造体の構築
    base = {
        "project": template["project"],
        "timestamp": datetime.datetime.now().isoformat(),
        "scene_context": scene_context,
        "context_type": context_type,
        "variation_id": variation_id,
        "identity_tag": identity_tag,
        "lora_settings": lora_settings,
        "global_overrides": template["global_overrides"],
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

    # プロンプト構築の論理（因果関係の記録）
    base["prompt_logic"] = {
        "applied_loras": [l['name'] for l in lora_settings],
        "identity_direction": identity_tag,
        "context_priority": "Physiological" if context_type == "paid" else "Relatability"
    }

    return base

if __name__ == "__main__":
    # テスト：資産CSVを読み込んで「公衆電話」の思想を生成
    try:
        thought = generate_thought("雨の公衆電話で誰かを待つ", context_type="paid")
        print(json.dumps(thought, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
