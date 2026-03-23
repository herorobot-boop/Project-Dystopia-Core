import os
import gc
import time
import torch
from pathlib import Path
from core.engines.thought_translator import ThoughtTranslator
from core.engines.comfy_api_bridge import ComfyAPIBridge
from llama_cpp import Llama

# =========================================================
# 🏛️ H-K9 Core: Main Omega Executor (Ver.3.5.1 Blackwell)
# =========================================================

class DystopiaCommander:
    def __init__(self):
        self.translator = ThoughtTranslator()
        self.bridge = ComfyAPIBridge(server_address="127.0.0.1:8888")
        self.vlm_path = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
        
    def execute_sequence(self, script_id):
        print(f"\n🐺 [H-K9] 執行開始シークエンス: {script_id}")

        # --- PHASE 1: 脳の覚醒 (LLM Inference) ---
        # 32GB VRAM のうち約 17GB を占有
        print("🧠 [Phase 1] Awakening Brain (Qwen 3.5 IQ4_XS)...")
        brain = Llama(
            model_path=self.vlm_path,
            n_gpu_layers=-1, # 5090 に全委託
            n_ctx=4096,
            jinja=True,
            verbose=False
        )
        
        # 聖典からの翻訳執行
        raw_physics_tags = self.translator.translate(script_id)
        
        # LLMによるタグの高密度化推論
        response = brain.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are the H-K9 Physics Engine. Expand the following tags into high-density anatomical and collision descriptions."},
                {"role": "user", "content": raw_physics_tags}
            ]
        )
        final_tags = response['choices'][0]['message']['content']
        
        # --- PHASE 2: 脳の破棄と浄化 (VRAM Swap) ---
        print("🧹 [Phase 2] Purging Brain. Freeing VRAM for Wan 2.2 Factory...")
        del brain
        gc.collect()
        time.sleep(1) # ドライバの解放待ち
        torch.cuda.empty_cache()
        print(f"✅ [VRAM] Blackwell 5090 is now clear. (Current tags: {final_tags[:100]}...)")

        # --- PHASE 3: 肉体の覚醒と射出 (API Bridge) ---
        # 32GB 全リソースを ComfyUI (Wan 2.2) へ譲渡
        print("🚀 [Phase 3] Injecting into 23,000-line Factory...")
        prompt_id = self.bridge.send_to_factory(final_tags)
        
        if prompt_id:
            print(f"📡 [Success] 射出完了。Prompt ID: {prompt_id}")
            return prompt_id
        else:
            print("❌ [Failure] 射出に失敗しました。")
            return None

if __name__ == "__main__":
    commander = DystopiaCommander()
    while True:
        cmd = input("\n[H-K9 Command Input] >> ").strip()
        if cmd.lower() in ["exit", "quit"]: break
        if cmd.startswith("V2_"):
            commander.execute_sequence(cmd)
        else:
            print("⚠️ [Wait] 合言葉は 'V2_' から開始してください。")
