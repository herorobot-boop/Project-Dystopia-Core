import json
import re
from pathlib import Path

class ThoughtTranslator:
    def __init__(self, dict_path="config/dictionary/h_k9_dictionary_V2_Final.json"):
        # RunPod上の絶対パスを優先解決
        self.base_dir = Path(__file__).resolve().parents[2]
        self.dict_full_path = self.base_dir / dict_path
        self.dictionary = {}
        self._load_dictionary()

    def _load_dictionary(self):
        """聖典V2（全5000件規模）をメモリアップロード"""
        if not self.dict_full_path.exists():
            print(f"⚠️ [Warning] Dictionary missing: {self.dict_full_path}")
            return
        with open(self.dict_full_path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
        print(f"📖 [H-K9] Sacred Dictionary Active. Size: {len(self.dictionary)} entries.")

    def translate(self, command):
        """合言葉を Blackwell 5090 向け高密度タグへ変換"""
        entry = self.dictionary.get(command)
        
        # 曖昧検索プロトコル（IDの微細な不一致を許容）
        if not entry:
            clean_cmd = command.replace("#", "").replace("_", "").lower()
            for k, v in self.dictionary.items():
                if clean_cmd in k.replace("#", "").replace("_", "").lower():
                    entry = v
                    break
        
        if not entry:
            return "logistics_simulation, industrial_texture, physically_based_rendering"

        detail = entry.get("detail", str(entry))
        physics = entry.get("physics", "standard_physics, tissue_displacement")

        # 物理演算重みの抽出
        weight_match = re.search(r"\((\d+\.\d+)\)", detail)
        intensity = weight_match.group(1) if weight_match else "1.3"

        # Qwen3.5 への高密度推論指令
        system_instruction = (
            f"Mandatory output: physics tags only. Input: {detail}, {physics}. "
            f"Parameters: (extremely detailed skin texture:{intensity}), (subsurface scattering:1.2), "
            f"(physically based fluid dynamics:1.4), cinematic 8k, raw photo."
        )
        return system_instruction

if __name__ == "__main__":
    translator = ThoughtTranslator()
    print(translator.translate("V2_改09_夢の国執行#28"))
