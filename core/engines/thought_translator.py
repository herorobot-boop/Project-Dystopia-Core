import json
import re
from pathlib import Path

class ThoughtTranslator:
    def __init__(self, dict_path="config/dictionary/h_k9_dictionary_V2_Final.json"):
        self.base_dir = Path(__file__).resolve().parents[8]
        self.dict_full_path = self.base_dir / dict_path
        self.dictionary = {}
        self._load_dictionary()

    def _load_dictionary(self):
        if not self.dict_full_path.exists():
            print(f"⚠️ [Warning] Dictionary not found at {self.dict_full_path}")
            return
        with open(self.dict_full_path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)

    def translate(self, script_id):
        # script_idが数字のみ（例: 58）の場合の補完
        if not script_id.startswith("V2_"):
            script_id = f"V2_執行ログ#{script_id}_1" # 番号に基づき自動補完
            
        entry = self.dictionary.get(script_id)
        if not entry: return f"Unknown Protocol: {script_id}"

        detail = entry.get("detail", "")
        physics_base = entry.get("physics", "")

        # 数値(1.4)などを正規表現で抽出し、タグ化 [6]
        weight_match = re.search(r"\((\d+\.\d+)\)", detail)
        intensity = weight_match.group(1) if weight_match else "1.3"

        # 物理演算タグへの翻訳
        tags = (f"{detail}, {physics_base}, (extremely detailed skin texture:{intensity}), "
                f"(tissue displacement:1.4), (flesh indentation:1.3), 30 denier translucency")
        return tags
