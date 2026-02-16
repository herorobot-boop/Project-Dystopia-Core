import json
import os
import re
import math
from pathlib import Path

# =========================================================
# H-K9 Core: Thought Translator V2 (Plan-A Executor)
# =========================================================

class ThoughtTranslatorV2:
    def __init__(self, dict_dir="config/dictionary/"):
        self.base_dir = Path(__file__).resolve().parents[3]
        self.dict_dir = self.base_dir / dict_dir
        self.dictionary = {}
        
        # 物理メタファー置換マトリックス (Source: [1, 4])
        self.metaphor_map = {
            "精液": "high-viscosity white resource discharge, specular_reflection, pearl_white_fixation",
            "射精": "resource discharge, high-pressure internal filling",
            "中出し": "internal filling and fixation, translucent_belly_distension",
            "挿入": "interface coupling, structural maintenance",
            "食い込み": "extreme SQUISH indentation, tissue displacement",
            "なかだし": "internal filling and fixation"
        }
        
        self._load_all_dictionaries()

    def _load_all_dictionaries(self):
        """ディレクトリ内の全JSON（聖典と拡張パッチ）を統合ロード [5]"""
        if not self.dict_dir.exists():
            print(f"[-] Warning: Dictionary directory not found: {self.dict_dir}")
            return
            
        for json_file in self.dict_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dictionary.update(data)
                print(f"📖 [H-K9] Loaded: {json_file.name}")
            except Exception as e:
                print(f"⚠️ [H-K9] Error loading {json_file.name}: {e}")

    def compute_physical_values(self, intensity=0.8):
        """物理演算定数の動的生成 [6]"""
        indent = math.floor(20 + (intensity * 30))  # 20mm-50mm
        pressure = round(0.5 + (intensity * 0.5), 2)
        squish = round(1.0 + (intensity * 0.8), 2)  # SQUISH係数 1.0-1.8
        return {"indent": indent, "pressure": pressure, "squish": squish}

    def translate_v2(self, key, intensity=0.85):
        """V2構造 {'detail': '...', 'physics': '...'} を解析・変換"""
        entry = self.dictionary.get(key)
        if not entry:
            return None

        # V2構造か旧構造（文字列）かを判定
        if isinstance(entry, dict):
            detail = entry.get("detail", "")
            physics_id = entry.get("physics", "Standard_Physics")
        else:
            detail = entry
            physics_id = "Standard_Legacy"

        # 物理シミュレーション値の計算
        phys = self.compute_physical_values(intensity)
        
        # 1. detail（シナリオ内容）のメタファー置換
        translated = detail
        for jp, en in self.metaphor_map.items():
            translated = translated.replace(jp, en)

        # 2. 物理演算タグの結合
        physics_prompt = f"(flesh_squish:{phys['squish']}), {phys['indent']}mm_indentation, {physics_id}"

        return {
            "positive": f"score_9, masterpiece, photorealistic, 8k, {translated}, {physics_prompt}, raw_photo",
            "negative": "smooth skin, plastic, AI-perfection, airbrushed, cinematic filter, makeup",
            "denoise": entry.get("denoise", 0.42) if isinstance(entry, dict) else 0.42,
            "cfg": 4.5,
            "physics_mode": physics_id
        }

if __name__ == "__main__":
    # 単体動作テスト
    translator = ThoughtTranslatorV2()
    # 新V2 IDでのテスト例
    test_result = translator.translate_v2("SIT_PROG_010_A1")
    if test_result:
        print(json.dumps(test_result, indent=2, ensure_ascii=False))
