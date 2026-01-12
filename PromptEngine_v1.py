class PromptEngine:
    def __init__(self):
        self.styles = {
            "Pony": "score_9, score_8_up, score_7_up, rating_explicit, (masterpiece:1.2), ",
            "Negative": "score_4, score_5, score_6, (worst quality:1.4), (low quality:1.4), lowres, blurry, "
        }

    def generate(self, p_type, character, scene, style_tags, extra):
        base_pos = self.styles["Pony"]
        base_neg = self.styles["Negative"]

        if p_type == "D": # Inpaint
            pos = f"{character}, {extra}, (highly detailed texture:1.2), {style_tags}"
            neg = base_neg + "clothes, fabric, background"
        elif p_type == "E": # Pose Master
            pos = f"{base_pos}{character}, {scene}, {style_tags}, {extra}, (identity swap:1.2)"
            neg = base_neg + "distorted body, extra limbs, incorrect pose"
        else: # Standard A/C
            pos = f"{base_pos}{character}, {scene}, {style_tags}, {extra}"
            neg = base_neg + "deformed hands, extra limbs"

        return {"positive": pos, "negative": neg}