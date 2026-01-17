import json
import os

class HK9_PromptEngine:
    def __init__(self):
        self.lora_map = self.load_json("lora_mapping.json")
        self.scene_map = self.load_json("scene_mapping.json")

    def load_json(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_command(self, scene_code):
        """
        シーンコードから全LoRAタグと強度を自動生成する
        """
        tags = self.scene_map.get(scene_code, [])
        if not tags:
            return "⚠️ Scene Code not found."

        lora_prompts = []
        for tag in tags:
            data = self.lora_map.get(tag)
            if data:
                # ComfyUI/A1111形式のLoRAタグを生成
                lora_prompts.append(f"<lora:{data['lora'][:-12]}:{data['strength']}>")
        
        final_prompt = ", ".join(lora_prompts)
        return f"【H-K9 Deployment: {scene_code}】\n{final_prompt}"

# 実行テスト
engine = HK9_PromptEngine()
print(engine.generate_command("school_scene"))
