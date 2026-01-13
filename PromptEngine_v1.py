# PromptEngine_v1.py (アップグレード版)
class PromptEngine:
    def __init__(self):
        # Ponyの深層心理を叩き起こすための「聖歌」
        self.pony_sacred_tags = "score_9, score_8_up, score_7_up, rating_explicit, (masterpiece:1.2), "
        self.negative_standard = "score_4, score_5, score_6, (worst quality:1.4), (low quality:1.4), lowres, blurry, "

    def generate(self, p_type, character, scene, style, extra):
        # 共通のネガティブ設定：服の残りカスや破綻を排除
        base_neg = self.negative_standard + "deformed hands, extra limbs, clothes, underwear, fabric, "

        if p_type == "D" or p_type == "D+":
            # 【Type D/D+専用】肌の質感と解剖学的正解を最優先するロジック
            pos = f"{character}, {extra}, (highly detailed skin:1.3), (realistic skin texture:1.2), {scene}, {style}"
            neg = base_neg + "missing nipples, blurred skin, plastic texture"
        
        elif p_type == "E":
            # 【Type E専用】ポーズ固定・アイデンティティ重視
            pos = f"{self.pony_sacred_tags}{character}, {scene}, {style}, {extra}, (perfect anatomy:1.1)"
            neg = base_neg
            
        else:
            # 【Type A/B/C専用】標準的な高密度生成
            pos = f"{self.pony_sacred_tags}{character}, {scene}, {style}, {extra}"
            neg = base_neg

        return {"positive": pos, "negative": neg}
