import json
import os

class ThoughtTranslator:
    def __init__(self, dict_dir="config/dictionary/"):
        self.dictionary = {}
        self.dict_dir = dict_dir
        # ディレクトリが存在しない場合は作成
        os.makedirs(self.dict_dir, exist_ok=True)
        self._load_all_dictionaries()
        
        # 物理メタファー変換マップ
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
            "腹部膨満": "Abdominal_Distension"
        }

    def _load_all_dictionaries(self):
        """ディレクトリ内の全JSONファイルを統合してロード（全文）"""
        for filename in os.listdir(self.dict_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.dict_dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # modificationsや各カテゴリを再帰的にアップデート
                        self.dictionary.update(data)
                        print(f"📖 [H-K9] Integrated Dictionary: {filename}")
                except Exception as e:
                    print(f"⚠️ [H-K9] Load Error {filename}: {e}")

    def translate(self, key_or_text):
        """辞書引きとメタファー変換を一括実行（全文）"""
        # 1. 辞書から該当するテキストを探す
        raw_text = self._deep_search(self.dictionary, key_or_text)
        
        # 2. メタファー変換
        translated = raw_text
        for k, v in self.mapping.items():
            translated = translated.replace(k, v)
        
        # 3. 物理・画質命令をスタック
        translated += ", photorealistic raw photo, 8k, highly detailed skin gloss, cinematic lighting"
        return translated

    def _deep_search(self, d, target):
        """ネストされた辞書内を再帰的に検索（全文）"""
        if target in d:
            res = d[target]
            return f"{res.get('name', '')} {res.get('effect', '')}" if isinstance(res, dict) else res
        for v in d.values():
            if isinstance(v, dict):
                res = self._deep_search(v, target)
                if res: return res
        return target
