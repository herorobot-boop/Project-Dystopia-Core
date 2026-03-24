import os
import sys
import json
import time
import torch
import gc
from pathlib import Path
from llama_cpp import Llama
import requests

# =========================================================
# 🏛️ Project Dystopia: Main Control Unit (v3.6 Final)
# =========================================================

class HK9CommandCenter:
    def __init__(self):
        self.llm_path = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
        self.extension_log = "/workspace/Project-Dystopia-Core/logs/video_extension_logic.json"
        self.automation_mode = False  # 自動化トグル
        self.pose_enabled = True      # ポーズ制御トグル

    def _vram_swap_brain(self, query):
        """【交互覚醒】脳（LLM）をロードし、思考後に即座にVRAMを更地にする"""
        print("🧠 [Thought] Awakening Qwen3.5 (Uncensored)...")
        llm = Llama(model_path=self.llm_path, n_gpu_layers=-1, n_ctx=4096)
        
        # タイポ修正済みURLと同等の内部処理でプロンプト生成
        prompt = f"System: あなたはH-K9執行官です。User: {query}\nAssistant:"
        output = llm(prompt, max_tokens=512)
        tags = output['choices'][0]['text']
        
        del llm
        gc.collect()
        torch.cuda.empty_cache()
        print("🧹 [VRAM] Brain Purged. Ready for Wan 2.2 / Z-Image.")
        return tags

    def render_process(self, tags, is_video=False):
        """ComfyUI APIへの射出と動画秒数管理"""
        duration = "5s" if not is_video else "10s (Extended)"
        print(f"🚀 [Render] {duration} Sequence: {tags[:30]}...")
        # 実際には WebSocket で完了を待機
        time.sleep(10) 
        return "output_asset_001.mp4"

    def video_extension_loop(self, base_asset, original_tags):
        """動画延長プロトコル：日本語指示を学習し、自動継ぎ足しを執行"""
        while True:
            if not self.automation_mode:
                feedback = input("H-K9 (次の展開/skip/auto_on) >> ")
                if feedback == "skip": break
                if feedback == "auto_on": self.automation_mode = True; continue
            else:
                feedback = "AUTO_GENERATE_NEXT_PHASE" # 蓄積データからQwenが自律判断

            # 指示の蓄積（司令官のこだわりを学習）
            with open(self.extension_log, "a") as f:
                json.dump({"instruction": feedback, "base_tags": original_tags}, f)
                f.write("\n")

            print(f"🔄 [Extension] 5秒延長を開始: {feedback}")
            self.render_process(original_tags, is_video=True)

    def run(self):
        print("\n" + "█"*40 + "\n🐺 H-K9 OMEGA COMMAND CENTER\n" + "█"*40)
        while True:
            cmd = input("H-K9 (ID/edit/pose_toggle/auto_toggle) >> ").strip()

            if cmd == "auto_toggle":
                self.automation_mode = not self.automation_mode
                print(f"🤖 Automation Mode: {self.automation_mode}"); continue
            
            if cmd == "pose_toggle":
                self.pose_enabled = not self.pose_enabled
                print(f"🦴 Pose Control: {self.pose_enabled}"); continue

            if cmd.startswith("edit"):
                # Grok型画像編集：言葉だけで既存画像を改変
                img_path = input("Target Image >> ")
                mod_query = input("Modify Instruction (日本語) >> ")
                tags = self._vram_swap_brain(f"Edit {img_path} with: {mod_query}")
                self.render_process(tags)
                continue

            # --- 通常執行（聖典ID入力） ---
            # ポーズ制御がONなら、ここで OpenPose Studio または「改」を介入させる
            if self.pose_enabled:
                p_choice = input("Pose Mode (改05/studio/none) >> ")
                if p_choice == "studio": print("🖱️ ComfyUIのGUIで骨格を調整してください...")

            tags = self._vram_swap_brain(f"Execute Protocol {cmd}")
            
            # 120点の静止画(Z-Image) -> 合格後 -> 動画化(Wan 2.2)
            asset = self.render_process(tags)
            self.video_extension_loop(asset, tags)

if __name__ == "__main__":
    center = HK9CommandCenter()
    center.run()
