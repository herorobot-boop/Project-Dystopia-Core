import os
import sys
import time
import torch
import gc
from llama_cpp import Llama
from pathlib import Path

# エンジンのインポート
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator
from comfy_api_bridge import ComfyAPIBridge

# =========================================================
# Project Dystopia: Main Control Unit (Omega-Blackwell)
# =========================================================

class HK9OperationCenter:
    def __init__(self):
        print("🐺 [H-K9] Operation Center: Active.")
        self.translator = ThoughtTranslator()
        self.bridge = ComfyAPIBridge()
        self.vlm_model = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"

    def _swap_awaken_brain(self, script_id):
        """【交互覚醒：思考】LLMをロードし、完了後にVRAMを更地にする [Omega-Blackwell]"""
        print(f"\n🧠 [Thought] Awakening Qwen3.5 for mission: {script_id}")
        llm = Llama(model_path=self.vlm_model, n_gpu_layers=-1, n_ctx=4096, jinja=True)
        
        raw_translation = self.translator.translate(script_id)
        prompt = f"USER: {raw_translation}\nASSISTANT:"
        output = llm(prompt, max_tokens=512)
        tags = output['choices']['text']
        
        # VRAM解放
        del llm
        gc.collect()
        torch.cuda.empty_cache()
        print("🧹 [VRAM] Brain purged. Resources assigned to Blackwell 5090.")
        return tags

    def run_loop(self):
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🐺 H-K9 HEAVY OPERATION CENTER: OMEGA-BLACKWELL")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        while True:
            mission = input("H-K9 >> ").strip()
            if mission.lower() in ["exit", "quit"]: break
            if mission.startswith("V2_"):
                # 1. 思想の覚醒
                physics_tags = self._swap_awaken_brain(mission)
                
                # 2. 工場への射出（Wan 2.2 現像）
                print(f"🚀 [Launch] Dispatching Protocol to Wan 2.2 Engine...")
                prompt_id = self.bridge.execute_payload(physics_tags)
                print(f"✅ Execution successful. Prompt ID: {prompt_id}")
            else:
                print("💡 'V2_' で始まる聖典IDを入力してください。")

if __name__ == "__main__":
    center = HK9OperationCenter()
    center.run_loop()
