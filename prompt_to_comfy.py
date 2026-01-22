import json
import random
from pathlib import Path
from prompt_builder import build_prompt

def build_comfy_payload(thought_json: dict, width=832, height=1216, seed=None, model="SDXL"):
    """
    思想JSONをComfyUIが解釈可能なデータ構造にパッキングする。
    """
    
    # 1. 最終プロンプトの翻訳（ポジティブ/ネガティブ）
    pos_prompt = build_prompt(thought_json)
    neg_prompt = build_prompt(thought_json, negative=True)

    # 2. ペイロード構築
    payload = {
        "meta_data": {
            "project": thought_json.get("project", "Project Dystopia"),
            "context": thought_json.get("context_type", "free"),
            "timestamp": thought_json.get("timestamp"),
            "variation_id": thought_json.get("variation_id")
        },
        "params": {
            "positive_prompt": pos_prompt,
            "negative_prompt": neg_prompt,
            "loras": thought_json.get("lora_settings", []),
            "resolution": {"width": width, "height": height},
            "seed": seed if seed is not None else random.randint(0, 10**16),
            "model_architecture": model
        }
    }

    return payload

if __name__ == "__main__":
    from thought_generator import generate_thought

    # テスト実行：深夜のコンビニ（Teaser）
    thought = generate_thought("深夜のコンビニ、駐車場、防犯カメラの視点", context_type="teaser")
    payload = build_comfy_payload(thought)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
