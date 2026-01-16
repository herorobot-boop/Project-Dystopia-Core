import json
import os

class PromptEngine:
    def __init__(self, mapping_path="lora_mapping.json"):
        self.pony_sacred_tags = "score_9, score_8_up, rating_explicit, (masterpiece:1.2), "
        self.negative_standard = "score_4, score_5, score_6, (worst quality:1.4), lowres, blurry, "
        self.lora_mapping = self.load_lora_mapping(mapping_path)

    def load_lora_mapping(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(f"⚠️ lora_mapping.json not found at {path}")
            return {}

    def resolve_lora(self, tag_code):
        entry = self.lora_mapping.get(tag_code)
        if entry:
            return f"<lora:{entry['lora']}:{entry['strength']}>"
        return ""

    def generate(self, p_type, character, scene, style, extra, structure_tags=None):
        base_neg = self.negative_standard + "deformed hands, extra limbs, clothes, fabric, "
        pos = ""
        neg = base_neg

        if p_type in ["D", "D+"]:
            pos = f"{character}, {extra}, (highly detailed skin:1.3), (realistic skin texture:1.2), {scene}, {style}"
            neg += "missing nipples, blurred skin, plastic texture"
        elif p_type == "E":
            pos = f"{self.pony_sacred_tags}{character}, {scene}, {style}, {extra}, (perfect anatomy:1.1)"
        else:
            pos = f"{self.pony_sacred_tags}{character}, {scene}, {style}, {extra}"

        # LoRA自動注入（構造タグに基づく）
        if structure_tags:
            for tag_code in structure_tags:
                lora = self.resolve_lora(tag_code)
                if lora:
                    pos += f", {lora}"

        return {"positive": pos.strip(", "), "negative": neg.strip(", ")}
