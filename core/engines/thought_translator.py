import json

class ThoughtTranslator:
    def __init__(self, dict_path="config/dictionary/h_k9_dictionary.json"):
        self.dict_path = dict_path
        with open(self.dict_path, "r", encoding="utf-8") as f:
            self.dictionary = json.load(f)

    def translate(self, command):
        """例: '行20' という入力を受け取り、詳細な物理プロンプトへ変換"""
        # 1. 辞書から該当項目を検索
        # ※辞書構造が {'category': {'id': 'text'}} の場合を想定
        target_text = ""
        for cat in self.dictionary.values():
            if command in cat:
                target_text = cat[command]
                break
        
        if not target_text:
            return f"High quality photo of a resource management scene, {command}"

        # 2. H-K9特有の「物理パラメータ」へ肉付け
        prompt = f"Photo-realistic, 8k, {target_text}, "
        prompt += "highly detailed skin texture, glossy white fluid coating, "
        prompt += "realistic body indentation, deep squish physics, "
        prompt += "intense lighting, cinematic shadows --ar 2:3"
        
        return prompt
