import json
import random
import sys
from pathlib import Path

# --- 神経接続：プロジェクトルートとカレントエンジンパスの特定 ---
BASE_DIR = Path(__file__).resolve().parents[2]
CURRENT_ENGINE_DIR = Path(__file__).resolve().parent

# --- 自走用インポート設定 ---
if str(CURRENT_ENGINE_DIR) not in sys.path:
    sys.path.append(str(CURRENT_ENGINE_DIR))

try:
    from prompt_builder import build_prompt
except ImportError as e:
    print(f"[-] Critical Error: prompt_builder.py not found in {CURRENT_ENGINE_DIR}")
    raise e

def build_comfy_payload(thought_json: dict, width=832, height=1216, seed=None, model="SDXL"):
    """
    思想JSONをComfyUIが解釈可能なデータ構造にパッキングする。
    [HERO's Logic Preserved: メタデータとパラメータの分離構造を維持]
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
    # --- テスト環境の動的解決 ---
    try:
        from thought_generator import generate_thought
        print(f"[*] Engine Path: {CURRENT_ENGINE_DIR}")
        
        # テスト実行：深夜のコンビニ（Teaser）
        test_scene = "深夜のコンビニ、駐車場、防犯カメラの視点"
        thought = generate_thought(test_scene, context_type="teaser")
        payload = build_comfy_payload(thought)

        print("\n🚀 ComfyUI Payload Delivery Test:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
    except ImportError as e:
        print(f"[-] ImportError: {e}. Check engine placement in core/engines/")
    except Exception as e:
        print(f"[-] Unexpected Error: {e}")
