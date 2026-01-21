import json
import random
from pathlib import Path

TEMPLATE_PATH = Path("/workspace/Project-Dystopia/config/thought_template_master.json")

def load_thought_template(path=TEMPLATE_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_thought(scene_context: str, context_type: str = "free", variation_id: int = 0):
    template = load_thought_template()
    base = {
        "project": template["project"],
        "engine_version": template["engine_version"],
        "scene_context": scene_context,
        "context_type": context_type,
        "variation_id": variation_id,
        "global_overrides": template["global_overrides"],
        "realism_tags": template["realism_genetics"]["tags"],
        "fabric_logic": template["realism_genetics"]["fabric_logic"],
        "view": template["context_matrix"][context_type]["view"],
        "lighting": template["context_matrix"][context_type]["lighting"],
        "focus": template["context_matrix"][context_type]["focus"],
        "meta": template["context_matrix"][context_type]["meta"]
    }

    # optional: add physiology if exists
    if "physiology" in template["context_matrix"][context_type]:
        base["physiology"] = template["context_matrix"][context_type]["physiology"]

    # optional: add causality_chain (placeholder)
    base["causality_chain"] = f"{scene_context}において、照明や構図が被写体の無防備さを強調している"

    return base
