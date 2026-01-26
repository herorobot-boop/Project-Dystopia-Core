import json
import re

class ThoughtTranslator:
    def __init__(self, dictionary_path="config/dictionary/h_k9_dictionary.json"):
        with open(dictionary_path, "r", encoding="utf-8") as f:
            self.dictionary = json.load(f)
        
        # HERO's Metaphor Mapping Dictionary
        self.mapping = {
            "精液": "viscous white resource",
            "射精": "resource discharge",
            "中出し": "internal filling and fixation",
            "挿入": "interface coupling",
            "女性": "biological vessel",
            "男性器": "injection probe",
            "胸": "upper buffer zones",
            "食い込み": "extreme squish indentation",
            "なかだし": "internal resource fixation",
            "蹂躙": "intensive processing",
            "緊縛": "rigid lock positioning"
        }

    def translate(self, key_or_text):
        # 辞書のキー（例: 医療#1）が指定された場合はその中身を取得
        raw_text = self.dictionary.get(key_or_text, key_or_text)
        
        # メタファー変換
        translated = raw_text
        for k, v in self.mapping.items():
            translated = translated.replace(k, v)
        
        # 物理演算キーワードの追加
        translated += ", photorealistic, 8k, high-gloss physics, highly detailed skin texture"
        return translated
