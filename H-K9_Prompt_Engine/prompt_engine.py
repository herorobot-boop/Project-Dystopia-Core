import json
import os
from datetime import datetime

class HK9_PromptEngine:
    def __init__(self, mapping_path="lora_mapping.json", scene_path="scene_mapping.json"):
        self.lora_map = self.load_json(mapping_path)
        self.scene_map = self.load_json(scene_path)

    def load_json(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def resolve_lora(self, tag_code, override_strength=None):
        entry = self.lora_map.get(tag_code)
        if entry:
            strength = override_strength if override_strength else entry['strength']
            return f"<lora:{entry['lora'].replace('.safetensors','')}:{strength}>"
        return ""

    def generate_command(self, scene_code, log_path="run_log.csv", overrides=None, output_path=None, notes=""):
        tags = self.scene_map.get(scene_code, [])
        if not tags:
            return f"⚠️ Scene Code '{scene_code}' not found."

        lora_prompts = []
        for tag in tags:
            strength_override = overrides.get(tag) if overrides else None
            lora = self.resolve_lora(tag, strength_override)
            if lora:
                lora_prompts.append(lora)

        final_prompt = ", ".join(lora_prompts)

        # ✅ ログ出力
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{scene_code},{final_prompt},{','.join(tags)},{output_path if output_path else ''},{notes}\n")

        return f"【H-K9 Deployment: {scene_code}】\n{final_prompt}"

    def generate_and_save(self, scene_code, output_dir="outputs", overrides=None, notes=""):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scene_code}_{timestamp}.png"
        output_path = os.path.join(output_dir, filename)
        prompt = self.generate_command(
            scene_code=scene_code,
            log_path="run_log.csv",
            overrides=overrides,
            output_path=output_path,
            notes=notes
        )
        return prompt
