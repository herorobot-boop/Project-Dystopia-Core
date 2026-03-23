import json
import os
import re
from pathlib import Path

# =========================================================
# H-K9 Core: Thought Translator v3.5 (Omega-Blackwell)
# =========================================================

class ThoughtTranslator:
    def __init__(self, dict_dir="config/dictionary/"):
        # プロジェクトルートからの相対パスを確定
        self.base_dir = Path(__file__).resolve().parents[2]
        self.dict_dir = self.base_dir / dict_dir
        self.dictionary = {}
        
        # H-K9 独自メタファー：事務的用語を物理シミュレーションタグへ変換
        self.mapping = {
            "精液/射精": "resource_insertion, viscous_fluid_coating, high_viscosity_liquid",
            "挿入/中出し": "interface_coupling, internal_resource_fixation, pressure_deformation",
            "女性/少女": "experimental_subject, vessel_unit, anatomical_precision",
            "男性器": "supply_probe, distribution_device, rigid_object_collision",
            "蹂躙/多人数": "multi_sector_processing, mass_logistics_audit, complex_interaction"
        }
        self._load_all_dictionaries()

    def _load_all_dictionaries(self):
        """ディレクトリ内の全JSON（聖典V2, extension等）を再帰的にマージ"""
        if not self.dict_dir.exists():
            print(f"⚠️ [Warning] Dictionary directory not found: {self.dict_dir}")
            return

        # 聖典V2、パッチ、拡張辞書をすべて取得
        json_files = sorted(self.dict_dir.glob("*.json"))
        for f in json_files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # 辞書がリスト形式か辞書形式かを確認してマージ
                    if isinstance(data, dict):
                        self.dictionary.update(data)
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "id" in item:
                                self.dictionary[item["id"]] = item
                print(f"📖 [Loaded] {f.name} (Current dict size: {len(self.dictionary)})")
            except Exception as e:
                print(f"❌ [Error] Failed to load {f.name}: {e}")

    def translate(self, command):
        """合言葉（V2_XXX）から Blackwell 5090 向けの物理演算プロンプトを錬成"""
        print(f"🔍 [H-K9] Translating command: {command}")
        
        # 1. 聖典からの直接検索
        entry = self.dictionary.get(command)
        
        # 2. 曖昧検索（ハッシュやアンダーバーの揺れを吸収）
        if not entry:
            clean_cmd = command.replace("#", "").replace("_", "").lower()
            for k, v in self.dictionary.items():
                if clean_cmd in k.replace("#", "").replace("_", "").lower():
                    entry = v
                    break

        if not entry:
            print(f"⚠️ [Unknown] {command} not found. Using generic logistics fallback.")
            return "logistics_simulation, high_fidelity, industrial_setting"

        # 3. コンテンツの抽出
        # 聖典が detail/physics 構造を持っていることを前提とする
        detail = ""
        if isinstance(entry, dict):
            detail = entry.get("detail", str(entry))
            physics = entry.get("physics", "standard_gravity, collision_detection")
        else:
            detail = str(entry)
            physics = "standard_gravity"

        # 4. H-K9 メタファーの物理置換執行
        for key, val in self.mapping.items():
            detail = detail.replace(key, val)

        # 5. 物理演算強度の自動抽出 (例: (1.4) という記述から重みを取得)
        weight_match = re.search(r"\((\d+\.\d+)\)", detail)
        intensity = float(weight_match.group(1)) if weight_match else 1.0

        # 6. Blackwell 5090 / Z-Image / Wan 2.2 向け最終プロンプト構築
        # 32GB VRAM を使い切るための高密度な質感指定を強制付与
        final_prompt = (
            f"{detail}, {physics}, (extremely detailed skin texture:1.3), "
            f"(subsurface scattering:1.2), (natural lighting:1.2), "
            f"physically_based_rendering, cinematic 8k photo, raw image --intensity {intensity}"
        )
        
        return final_prompt

if __name__ == "__main__":
    # 単体テスト用
    translator = ThoughtTranslator()
    test_cmd = "V2_執行ログ#151_1"
    print(f"\n[Result]\n{translator.translate(test_cmd)}")
