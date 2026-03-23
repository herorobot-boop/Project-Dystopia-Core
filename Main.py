import os
import sys
import time
import torch
import gc
from llama_cpp import Llama
from pathlib import Path

# エンジン・パスの強制解決
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
        # Blackwell 専用 IQ4_XS 量子化モデル
        self.vlm_model = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"

    def _swap_awaken_brain(self, script_id):
        """【交互覚醒】LLM をロードし、推論後に VRAM を完全浄化する [Omega-Blackwell]"""
        print(f"\n🧠 [Thought] Awakening Qwen3.5 IQ4_XS: {script_id}")
        
        # Blackwell 5090 に全レイヤー(64+)をオフロード
        llm = Llama(
            model_path=self.vlm_model, 
            n_gpu_layers=-1, 
            n_ctx=4096, 
            jinja=True,
            verbose=False
        )

        raw_translation = self.translator.translate(script_id)
        prompt = f"USER: {raw_translation}\nASSISTANT:"
        
        # 思想の現像
        output = llm(prompt, max_tokens=1024)
        tags = output['choices'][0]['text']

        # 【軍律】VRAM の徹底排除
        del llm
        llm = None # 参照カウントを確実にゼロへ
        gc.collect()
        time.sleep(2.0) # ドライバレベルの解放待機
        torch.cuda.empty_cache()
        
        print("🧹 [VRAM] Brain purged. 32GB Territory is now Open for Factory Injection.")
        return tags

    def run_loop(self):
        print("\n" + "█"*60)
        print("      H-K9 HEAVY OPERATION CENTER: OMEGA-BLACKWELL V3.5.1")
        print("      STATUS: READY FOR MASS LOGISTICS AUDIT")
        print("█"*60)

        while True:
            try:
                mission = input("\nH-K9 >> ").strip()
                if not mission: continue
                if mission.lower() in ["exit", "quit"]: break
                
                if mission.startswith("V2_"):
                    # Phase 1: 思想翻訳 (LLM 覚醒)
                    physics_tags = self._swap_awaken_brain(mission)
                    print(f"✨ [Tags] Physics Output: {physics_tags[:100]}...")

                    # Phase 2: 物理現像 (ComfyUI 射出)
                    print(f"🚀 [Launch] Dispatching Protocol to Wan 2.2 Factory...")
                    prompt_id = self.bridge.execute_payload(physics_tags)
                    
                    if prompt_id:
                        print(f"📡 [Confirmed] Execution started. Prompt ID: {prompt_id}")
                    else:
                        print("❌ [Error] Injection failed. Check Factory port 8888.")
                else:
                    print("⚠️ [Wait] 合言葉は 'V2_' で開始してください。")
            except KeyboardInterrupt:
                print("\n👋 [Termination] Sequence interrupted. Cooling down Blackwell 5090...")
                break

if __name__ == "__main__":
    center = HK9OperationCenter()
    center.run_loop()
