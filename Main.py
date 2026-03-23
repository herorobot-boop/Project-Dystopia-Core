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
        print("🐺 [H-K9] Operation Center: Level 5 Authority Active.")
        self.translator = ThoughtTranslator()
        self.bridge = ComfyAPIBridge()
        # Blackwell 向け IQ4_XS モデル
        self.vlm_model = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"

    def _swap_awaken_brain(self, script_id):
        """【交互覚醒：思考】LLMを覚醒させ、完了後にVRAMを完全に浄化する [Omega-Blackwell]"""
        print(f"\n🧠 [Thought] Awakening Qwen3.5 IQ4_XS for mission: {script_id}")
        
        # 5090 Blackwell に全レイヤーを射出
        llm = Llama(
            model_path=self.vlm_model, 
            n_gpu_layers=-1, 
            n_ctx=4096, 
            jinja=True,
            verbose=False
        )

        raw_translation = self.translator.translate(script_id)
        # 高密度タグへの変換推論
        prompt = f"USER: {raw_translation}\nASSISTANT:"
        output = llm(prompt, max_tokens=1024)
        tags = output['choices'][0]['text']

        # 【軍律】VRAMの徹底浄化
        del llm
        gc.collect()
        time.sleep(1.5) # VRAM解放の物理待機
        torch.cuda.empty_cache()
        
        print("🧹 [VRAM] Brain purged. 32GB Territory is now Open for Blackwell Factory.")
        return tags

    def run_loop(self):
        print("\n" + "█"*60)
        print("      H-K9 HEAVY OPERATION CENTER: OMEGA-BLACKWELL V3.1")
        print("      STATUS: READY FOR MASS LOGISTICS AUDIT")
        print("█"*60)

        while True:
            mission = input("\nH-K9 >> ").strip()
            if not mission: continue
            if mission.lower() in ["exit", "quit"]: break
            
            if mission.startswith("V2_"):
                # 1. 思想の覚醒（LLMフェーズ）
                physics_tags = self._swap_awaken_brain(mission)
                print(f"✨ [Tags] Physics Engine Output: {physics_tags[:150]}...")

                # 2. 工場への射出（Wan 2.2 現像フェーズ）
                print(f"🚀 [Launch] Dispatching Protocol to Wan 2.2 Factory Engine...")
                prompt_id = self.bridge.execute_payload(physics_tags)
                
                if prompt_id:
                    print(f"📡 [Confirmed] Execution started. Prompt ID: {prompt_id}")
                else:
                    print("❌ [Error] Injection failed. Check ComfyUI status.")
            else:
                print("⚠️ [Wait] 合言葉は 'V2_' で開始してください。")

if __name__ == "__main__":
    center = HK9OperationCenter()
    center.run_loop()
