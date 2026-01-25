class PromptEngine:
    def __init__(self):
        self.pony_sacred_tags = "score_9, score_8_up, rating_explicit, (masterpiece:1.2), "
        self.negative_standard = "score_4, score_5, score_6, (worst quality:1.4), lowres, blurry, "
        # 思想を具現化するLoRA辞書
        self.lora_presets = {
            "[ANTI_MELT]": "<lora:structure_fixer_v1:0.6>",
            "[REAL_SKIN]": "<lora:detailed_skin_texture:0.7>",
            "[POSE_FIX]": "<lora:perfect_anatomy_fix:0.5>"
        }

    def apply_lora_presets(self, prompt):
        # タグを検索して置換。見つかれば末尾にLoRAを追加。
        for tag, lora in self.lora_presets.items():
            if tag in prompt:
                prompt = prompt.replace(tag, "").strip(", ") + ", " + lora
        return prompt.strip(", ")

    def generate(self, p_type, character, scene, style, extra):
        base_neg = self.negative_standard + "deformed hands, extra limbs, clothes, fabric, "

        if p_type in ["D", "D+"]:
            # D/D+ は局所修正用のため、Ponyの基本タグを除外し詳細を優先
            pos = f"{character}, {extra}, (highly detailed skin:1.3), (realistic skin texture:1.2), {scene}, {style}"
            neg = base_neg + "missing nipples, blurred skin, plastic texture"
        elif p_type == "E":
            # E はポーズ固定用
            pos = f"{self.pony_sacred_tags}{character}, {scene}, {style}, {extra}, (perfect anatomy:1.1)"
            neg = base_neg
        else:
            # A は基本のFlux+Pony
            pos = f"{self.pony_sacred_tags}{character}, {scene}, {style}, {extra}"
            neg = base_neg

        pos = self.apply_lora_presets(pos)
        return {"positive": pos, "negative": neg}
