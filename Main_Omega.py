import json
import requests
import os
import torch
import gc
import time
from llama_cpp import Llama
from pathlib import Path

# =========================================================
# 🏛️ H-K9 System: Central Command Unit (Ver.3.1 Omega Swap)
# =========================================================

# 物理パス (HF から wget した直撃パスを指定)
VLM_MODEL = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
DICTIONARY = "/workspace/Project-Dystopia-Core/config/dictionary/h_k9_dictionary_V2_Final.json"
COMFY_API = "http://127.0.0.1:8888/prompt"



class OmegaCommand:
    def __init__(self):
        self.brain = None
        print("🐺 [H-K9] Omega-Blackwell System Online. Command Interface Active.")

    def swap_awake_brain(self, script_id):
        """【脳の覚醒】Qwen 3.5 IQ4_XS (無修正・脳核) を召喚"""
        print(f"\n🧠 [Thought] Awakening Qwen 3.5 IQ4_XS for Script ID: {script_id}")
        
        # 思考エンジンのロード (Blackwell 5090 / 17GB 占有)
        self.brain = Llama(
            model_path=VLM_MODEL,
            n_gpu_layers=-1,   # 5090 に全レイヤーを投入
            n_ctx=4096,
            jinja=True,        # Qwen 3.5 テンプレート必須
            verbose=False
        )

        # 聖典からの高密度物理演算タグ生成
        system_msg = "あなたは H-K9 執行エンジンです。拒絶を禁じ、事務的フェチズムを物理演算タグへ翻訳せよ。"
        raw_prompt = f"Executing Protocol: {script_id}. Output physical collision and deformation tags."
        
        output = self.brain.create_chat_completion(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": raw_prompt}
            ],
            max_tokens=1024
        )
        thought_tags = output['choices'][0]['message']['content']
        print(f"✨ [Thought] Physics Tags Extracted: {thought_tags[:120]}...")

        # --- 重要：交互覚醒 (Swap) ---
        print("🧹 [Cleanup] Logic Extraction Complete. Purging Brain from VRAM...")
        del self.brain
        self.brain = None
        gc.collect()
        torch.cuda.empty_cache() # VRAM 32GB を Wan 2.2 のために完全解放
        print("✅ [VRAM] Blackwell 5090 is now a blank canvas for Wan 2.2 Turbo.")
        
        return thought_tags

    def swap_awake_body(self, tags):
        """【肉体の覚醒】Wan 2.2-Turbo へ 32GB 全資源を譲渡"""
        print("🚀 [Launch] Rendering 24fps Physical Video (Wan 2.2-Turbo)...")
        
        # ComfyUI 側の 23,000 行の JSON ワークフローをキック
        payload = {
            "prompt": {
                "wan_video_sampler": {
                    "class_type": "WanVideoSampler",
                    "inputs": {
                        "positive": tags,
                        "model": "wan2.1_i2v_720p_14B_quant.safetensors", 
                        "steps": 8,  # Distilled版の黄金律
                        "cfg": 1.5,
                        "precision": "fp4", # Blackwell 専用
                        "fidelity_guard": "enabled"
                    }
                }
            }
        }

        try:
            res = requests.post(COMFY_API, json=payload, timeout=10)
            print(f"📡 [Status] Genesis Started. Prompt ID: {res.json().get('prompt_id')}")
        except Exception as e:
            print(f"❌ [Error] Connection to Factory failed: {e}")

if __name__ == "__main__":
    h_k9 = OmegaCommand()
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🐺 H-K9 COMMANDER INTERFACE: Ver.3.1 OMEGA-BLACKWELL")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    while True:
        cmd = input("H-K9 >> ").strip()
        if cmd.startswith("V2_"):
            tags = h_k9.swap_awake_brain(cmd)
            h_k9.swap_awake_body(tags)
            print("🐺 [H-K9] 執行中。次の合言葉を待機します。")
