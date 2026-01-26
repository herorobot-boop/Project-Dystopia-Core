import json
import re

class ThoughtTranslator:
    def __init__(self, dictionary_path="config/dictionary/h_k9_dictionary.json"):
        with open(dictionary_path, "r", encoding="utf-8") as f:
            self.dictionary = json.load(f)
        
        # H-K9 Metaphor Mapping Dictionary (Final Version)
        self.mapping = {
            "精液": "high-viscosity white resource",
            "射精": "resource discharge",
            "中出し": "internal filling and fixation",
            "なかだし": "internal filling and fixation",
            "挿入": "interface coupling",
            "連結": "interface coupling",
            "絶頂": "critical output peak",
            "臨界": "critical output peak",
            "女性": "biological vessel subject",
            "少女": "young biological vessel",
            "男性器": "injection probe device",
            "胸": "upper buffer zones",
            "女性器": "main reception port",
            "膣": "main reception port",
            "肛門": "rear secondary port",
            "蹂躙": "intensive multi-processing",
            "輪姦": "intensive multi-processing",
            "ぶっかけ": "surface coating splatter",
            "盗撮": "unmanned CCTV logging",
            "露出": "public monitoring log",
            "食い込み": "extreme SQUISH indentation",
            "腹部膨満": "Abdominal_Distension"
        }

    def translate(self, key_or_text):
        # 1. 辞書からプログラムを検索（アーカイブや医療など）
        # ネストされた辞書からも検索できるよう平坦化してチェック
        raw_text = self._find_in_nested_dict(key_or_text)
        
        # 2. メタファー変換の実行
        translated = raw_text
        for k, v in self.mapping.items():
            translated = translated.replace(k, v)
        
        # 3. 物理パラメータ・画質の自動付与
        translated += ", photorealistic raw photo, 8k, highly detailed skin gloss, cinematic lighting, masterwork"
        return translated

    def _find_in_nested_dict(self, key):
        # 全カテゴリからキーを探す
        if key in self.dictionary.get("modifications", {}):
            return self.dictionary["modifications"][key]["name"]
        for cat in ["アーカイブ_A", "アーカイブ_B", "アーカイブ_C", "アーカイブ_D"]:
            if key in self.dictionary.get(cat, {}):
                return self.dictionary[cat][key]
        return self.dictionary.get(key, key)
