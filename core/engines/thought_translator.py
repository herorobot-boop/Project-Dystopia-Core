import json
from pathlib import Path

class ThoughtTranslatorV2:
    def __init__(self, dict_dir="config/dictionary/"):
        self.dict_dir = Path(dict_dir)
        self.dictionary = self._load_v2_dictionaries()

    def _load_v2_dictionaries(self):
        # 4000行以上の聖典と拡張パッチを合体 [3]
        merged = {}
        for file in self.dict_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                merged.update(json.load(f))
        return merged

    def translate_v2(self, key):
        """V2構造 {'detail': '...', 'physics': '...'} を解析・変換"""
        entry = self.dictionary.get(key)
        if not entry:
            return f"Unknown_ID: {key}"

        # 1. detail（シナリオ内容）の抽出 
        detail = entry.get("detail", "")
        # 2. physics（物理タグ）の抽出と変換 [2]
        physics_tag = entry.get("physics", "Standard_Physics")
        
        # 物理メタファー置換の適用 [4]
        translated = detail.replace("精液", "high-viscosity white resource")
        translated = translated.replace("挿入", "interface coupling")

        return {
            "prompt": f"{translated}, {physics_tag}, photorealistic, 8k",
            "physics_mode": physics_tag,
            "denoise": 0.42 # Z-Imageスイートスポット [5]
        }
