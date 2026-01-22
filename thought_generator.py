import json
import datetime
from pathlib import Path

# パスの設定
BASE_DIR = Path("/workspace/Project-Dystopia")
TEMPLATE_PATH = BASE_DIR / "config/thought_template_master.json"

def load_thought_template(path=TEMPLATE_PATH):
    """マスターテンプレートを読み込む"""
    if not path.exists():
        raise FileNotFoundError(f"Template not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_thought(scene_context: str, context_type: str = "free", variation_id: int = 0):
    """
    指定されたシーンと思想文脈に基づき、因果関係を含んだ思想JSONを生成する。
    """
    template = load_thought_template()
    
    # コンテキスト情報の抽出
    if context_type not in template["context_matrix"]:
        context_type = "free"  # デフォルト
    
    ctx = template["context_matrix"][context_type]
    genetics = template["realism_genetics"]
    
    # 基本構造の構築
    base = {
        "project": template["project"],
        "timestamp": datetime.datetime.now().isoformat(),
        "scene_context": scene_context,
        "context_type": context_type,
        "variation_id": variation_id,
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

    # 生理反応の追加（Paid/Teaser用）
    if "physiology" in ctx:
        base["physiology_detail"] = ctx["physiology"]

    # --- 核心部: 因果関係（Causality）の論理重み付け ---
    # AIが「なぜこの描写が必要か」を理解するためのロジック
    base["prompt_construction_logic"] = {
        "causality_chain": f"The scene '{scene_context}' dictates the physical state. "
                           f"The {ctx['focus']} focus requires a {ctx['view']} perspective.",
        
        "hierarchical_priority": [
            "1. Physical_Occlusion (Depth)", # 遮蔽による覗き見感
            "2. Physiological_Response (Vitality)", # 生理反応による生々しさ
            "3. Optical_Imperfection (UGC_Reality)" # 光学的ノイズによる実写感
        ],
        
        "interaction_rule": (
            f"Apply '{genetics['fabric_logic']['material_interaction']}' "
            f"triggered by the action '{genetics['fabric_logic']['action_state']}'."
        )
    }

    return base

if __name__ == "__main__":
    # テスト出力: Paid文脈での「放課後の教室」
    test_thought = generate_thought(
        scene_context="放課後の無人の教室、夕日", 
        context_type="paid", 
        variation_id=777
    )
    
    print(json.dumps(test_thought, indent=2, ensure_ascii=False))
