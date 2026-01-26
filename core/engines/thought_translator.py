import json
import os

class ThoughtTranslator:
    def __init__(self, dict_dir="config/dictionary/"):
        self.dictionary = {}
        self.dict_dir = dict_dir
        # 指定ディレクトリ内の全JSONを読み込んで合体させる
        self._load_all_dictionaries()
        
        # メタファー変換マップ（コード内にハードコードしておくのが一番安全です）
        self.mapping = {
            "精液": "high-viscosity white resource",
            "射精": "resource discharge",
            "中出し": "internal filling and fixation",
            "なかだし": "internal filling and fixation",
            "挿入": "interface coupling",
            "連結": "interface coupling",
            "絶頂": "critical output peak",
            "女性": "biological vessel subject",
            "男性器": "injection probe device",
            "胸": "upper buffer zones",
            "食い込み": "extreme SQUISH indentation",
            "腹部膨満": "Abdominal_Distension",
            "巨乳": "breast_enlargement_p200",
            "M字開脚": "m_pose_fixed"
        }

    def _load_all_dictionaries(self):
        """ディレクトリ内の全JSONを統合"""
        for filename in os.listdir(self.dict_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.dict_dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.dictionary.update(data)
                        print(f"📖 [H-K9] Loaded: {filename}")
                except Exception as e:
                    print(f"⚠️ [H-K9] Error loading {filename}: {e}")

    def translate(self, key_or_text):
        # 1. 統合辞書からテキストを取得（キーが見つからなければそのまま）
        raw_text = self._find_value(key_or_text)
        
        # 2. メタファー変換
        translated = raw_text
        for k, v in self.mapping.items():
            translated = translated.replace(k, v)
        
        # 3. 物理パラメータの付与
        translated += ", photorealistic, 8k, high-gloss skin, cinematic lighting"
        return translated

    def _find_value(self, key):
        # ネストされた構造（modificationsの中など）も再帰的に探す
        def search(d, target):
            if target in d: return d[target]
            for v in d.values():
                if isinstance(v, dict):
                    res = search(v, target)
                    if res: return res
            return None
        
        result = search(self.dictionary, key)
        # もし辞書に「改XX」があり、その中に"name"や"effect"があれば結合
        if isinstance(result, dict):
            return f"{result.get('name', '')} {result.get('effect', '')}"
        return result if result else key

# 執行
# translator = ThoughtTranslator()
# print(translator.translate("#44_警察24時"))
