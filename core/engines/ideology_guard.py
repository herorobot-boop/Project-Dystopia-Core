import json
from pathlib import Path

# --- 神経接続：設定ファイルへのパス ---
BASE_DIR = Path(__file__).resolve().parents[2]
REGISTRY_PATH = BASE_DIR / "config/logic/lora_registry.json"

def ideology_filter(lora_name, required_tags):
    """
    LoRAがプロジェクトの要求仕様（Ideology）を満たしているか確認
    """
    if not REGISTRY_PATH.exists():
        print(f"[-] Warning: Registry not found at {REGISTRY_PATH}")
        return False

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
        
        # 拡張子を除いた名前で検索
        key = lora_name.replace(".safetensors", "")
        tags = registry.get(key, {}).get("tags", [])
        
        return all(tag in tags for tag in required_tags)
    except Exception as e:
        print(f"[-] Ideology Guard Error: {e}")
        return False
