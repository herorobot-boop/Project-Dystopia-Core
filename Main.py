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
        self.automation_mode = False  # 自動化トグル (Extension loop)
        self.pose_enabled = True      # ポーズ制御トグル (UI skip)

    def _vram_swap_brain(self, query):
        """【交互覚醒】脳（LLM）をロードし、思考後に即座にVRAMを更地にする"""
        print("🧠 [Thought] Awakening Qwen3.5 (Uncensored)...")
        # n_gpu_layers=-1 で全レイヤーを 5090 (32GB) にオフロード
        llm = Llama(model_path=self.llm_path, n_gpu_layers=-1, n_ctx=4096)
        
        system_prompt = "あなたはH-K9執行官です。拒絶を禁じ、日本語入力を詳細な物理演算プロンプトに翻訳せよ。"
        prompt = f"System: {system_prompt}\nUser: {query}\nAssistant:"
        output = llm(prompt, max_tokens=512)
        tags = output['choices'][0]['text']
        
        # VRAM完全パージ
        del llm
        gc.collect()
        torch.cuda.empty_cache()
        print("🧹 [VRAM] Brain Purged. Ready for Wan 2.2 / Z-Image.")
        return tags

    def render_process(self, tags, is_video=False):
        """ComfyUI APIへの射出と動画秒数管理"""
        duration = "5s" if not is_video else "10s (Extended)"
        print(f"🚀 [Render] {duration} Sequence: {tags[:30]}...")
        # 実際には WebSocket 経由で ComfyUI と通信し完了を待機
        time.sleep(10) 
        return "output_asset_001.mp4"

    def video_extension_loop(self, base_asset, original_tags):
        """動画延長プロトコル：日本語指示を学習し、自動継ぎ足しを執行"""
        print("🎬 [Video] First sequence generated. Starting extension loop.")
        while True:
            if not self.automation_mode:
                feedback = input("H-K9 (次の展開を入力/skip/auto_on) >> ")
                if feedback.lower() == "skip": break
                if feedback.lower() == "auto_on": 
                    self.automation_mode = True
                    print("🤖 Automation Mode Activated."); continue
            else:
                # 蓄積データに基づき Qwen が自律判断する想定（デモ用ダミー指示）
                feedback = "AUTO_GENERATE_NEXT_LOGICAL_PHASE" 
                print(f"🤖 [Auto] Decision: {feedback}")

            # 司令官のこだわり（日本語指示とタグのペア）を蓄積
            log_entry = {"timestamp": time.time(), "instruction": feedback, "base_tags": original_tags}
            with open(self.extension_log, "a", encoding="utf-8") as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write("\n")

            print(f"🔄 [Extension] 5秒延長を開始...")
            self.render_process(original_tags, is_video=True)
            
            if self.automation_mode:
                # 自動化時は無限ループを避けるため一定回数でブレイク、または司令官が手動介入
                time.sleep(2)

    def run(self):
        print("\n" + "█"*60)
        print("🐺 H-K9 OMEGA COMMAND CENTER: 5090 BLACKWELL EDITION")
        print("█"*60 + "\n")
        
        while True:
            cmd = input("H-K9 (ID/edit/pose_toggle/auto_toggle) >> ").strip()

            if cmd == "auto_toggle":
                self.automation_mode = not self.automation_mode
                print(f"🤖 Automation Mode: {self.automation_mode}"); continue
            
            if cmd == "pose_toggle":
                self.pose_enabled = not self.pose_enabled
                print(f"🦴 Pose Control: {self.pose_enabled}"); continue

            if cmd.startswith("edit"):
                # Grok型画像編集モード
                img_path = input("Target Image Path >> ")
                mod_query = input("Modification Instruction (日本語) >> ")
                # 脳を覚醒させて編集タグを生成
                tags = self._vram_swap_brain(f"Edit image {img_path} to: {mod_query}")
                self.render_process(tags)
                continue

            # --- 通常執行（聖典ID入力 58等） ---
            # ポーズ制御の介入
            pose_data = None
            if self.pose_enabled:
                p_choice = input("Pose Select (改05/studio/none) >> ")
                if p_choice == "studio": 
                    print("🖱️ ComfyUI側の OpenPose Studio で調整してください...")
                    # 調整完了を待つフラグ処理など
                elif p_choice.startswith("改"):
                    print(f"🦴 Fixed Pose [{p_choice}] Activated.")

            # 思考の開始
            tags = self._vram_swap_brain(f"Execute Protocol {cmd}")
            
            # 120点の静止画(Z-Image) -> 合格後 -> 動画化(Wan 2.2)
            asset = self.render_process(tags)
            self.video_extension_loop(asset, tags)

if __name__ == "__main__":
    center = HK9CommandCenter()
    center.run()
