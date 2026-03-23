import json
import re
from pathlib import Path

class ThoughtTranslator:
    def __init__(self, dict_path="config/dictionary/h_k9_dictionary_V2_Final.json"):
        self.base_dir = Path(__file__).resolve().parents[13]
        self.dict_full_path = self.base_dir / dict_path
        self.dictionary = {}
        self._load_dictionary()

    def _load_dictionary(self):
        """聖典V2（4000行）をロード"""
        if not self.dict_full_path.exists():
            print(f"⚠️ [Warning] Dictionary not found at {self.dict_full_path}")
            return
        with open(self.dict_full_path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
        print(f"📖 [H-K9] Sacred Dictionary Loaded. Size: {len(self.dictionary)} entries.")

    def translate(self, command):
        """合言葉（例：V2_執行ログ#151_1）を物理タグへ変換"""
        entry = self.dictionary.get(command)
        if not entry:
            return f"Unknown Protocol: {command}"

        detail = entry.get("detail", "")
        physics = entry.get("physics", "standard_physics")

        # 物理演算数値の自動抽出（1.4などの重みを強調プロンプトへ変換） [14, 15]
        weight_match = re.search(r"\((\d+\.\d+)\)", detail)
        intensity = weight_match.group(1) if weight_match else "1.3"

        # Qwen3.5 への流し込み用プロンプト構築 [12]
        system_instruction = (
            f"Convert to high-density physics tags: {detail}, {physics}. "
            f"Focus on: (extremely detailed skin texture:{intensity}), (subsurface scattering:1.2), "
            f"(tissue displacement:1.3), 30 denier translucency."
        )
        return system_instruction

if __name__ == "__main__":
    translator = ThoughtTranslator()
    print(translator.translate("V2_改09_夢の国執行#28"))
