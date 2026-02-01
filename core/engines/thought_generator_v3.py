# =========================================================
# H-K9 Core: Thought Generator v3.0 (Z-Image/5090 Optimized)
# =========================================================
import json
import os

class ThoughtEngine:
    def __init__(self):
        # 聖典：物理シミュレーション変換辞書
        self.dictionary = {
            "挿入": "Interface coupling, intensive processing, structural maintenance",
            "精液": "High-viscosity white resource, resource discharge, specular_reflection:1.3",
            "食い込み": "Extreme SQUISH indentation, 30mm indentation depth, flesh overlap:1.4",
            "中出し": "Internal filling and fixation, translucent_belly_distension",
            "背景": "smartphone snap-shot, lens flare, digital noise, raw handheld photo"
        }

    def translate_thought(self, raw_text):
        """
        日本語の欲望を、物理演算パラメータを伴う英語プロンプトへ変換
        """
        processed_text = raw_text
        for jp, en in self.dictionary.items():
            processed_text = processed_text.replace(jp, en)
        
        # Z-Image「引き算の美学」プロンプト構築
        base_quality = "score_9, photorealistic, 8k, extremely detailed skin, subsurface scattering"
        negative = "smooth skin, plastic, AI-perfection, airbrushed, studio lighting"
        
        # 最終的な思想構造
        payload = {
            "positive": f"{base_quality}, {processed_text}",
            "negative": negative,
            "cfg": 4.2,
            "denoise": 0.42, # Z-Imageスイートスポット
            "sampler": "dpmpp_2m_sde_gpu",
            "scheduler": "karras"
        }
        return payload

    def run_interactive(self):
        print("🐺 [H-K9] Thought Engine Active. Waiting for HERO's command...")
        while True:
            user_input = input("\n👉 Enter Thought (or 'exit'): ")
            if user_input.lower() == 'exit': break
            
            result = self.translate_thought(user_input)
            print("\n✨ Generated Payload (Ready for ComfyUI):")
            print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    engine = ThoughtEngine()
    engine.run_interactive()
