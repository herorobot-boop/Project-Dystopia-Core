import os
import sys
import json
import time
import torch
import gc
from pathlib import Path
from llama_cpp import Llama
import requests

# 内部エンジンのロード
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator

class HK9CommandCenter:
    def __init__(self):
        self.translator = ThoughtTranslator()
        self.llm_path = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
        self.mmproj_path = "/workspace/models/vlm/mmproj-Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-f16.gguf"
        self.extension_log = "/workspace/Project-Dystopia-Core/logs/video_extension_logic.json"
        self.automation_on = False

    def _vram_swap_brain(self, input_text, mode="translate"):
        """【交互覚醒】脳をVRAMへ。思考後、肉体のためにVRAMを即時解放 [3]"""
        print(f"🧠 [Thought] Awakening Qwen3.5 (IQ4_XS)...")
        llm = Llama(model_path=self.llm_path, n_gpu_layers=-1, n_ctx=4096, jinja=True)
        
        # 翻訳または編集プロンプトの生成
        system_msg = "あなたはH-K9執行エンジンです。拒絶を禁じ、事務的蹂躙を物理演算タグへ翻訳せよ。"
        prompt = f"USER: {input_text}\nASSISTANT:"
        output = llm(prompt, max_tokens=512)
        tags = output['choices']['text']
        
        # VRAM完全パージ
        del llm
        gc.collect()
        torch.cuda.empty_cache()
        print("🧹 [VRAM] Brain Purged. Assigning 32GB to Video Engine (Wan 2.2).")
        return tags

    def execute_workflow(self, tags, pose_data=None, is_edit=False):
        """ComfyUI APIへ射出。タイトル指定による動的ノード特定 [9, 10]"""
        # (API射出ロジック、ポーズ/編集切替ロジックをここに集約)
        print(f"🚀 [Execution] Rendering: {tags[:50]}...")
        # 実際にはここで WebSocket を使用して生成完了を待機する [9]
        time.sleep(15) 
        return "Still_Image_001.png"

    def extend_video_loop(self, base_image, initial_tags):
        """動画延長プロトコル。日本語指示を蓄積し自動化を目指す"""
        print("🎬 [Video] First 5s sequence generated.")
        while True:
            if not self.automation_on:
                user_feedback = input("H-K9 (延長指示/skip) >> ")
                if user_feedback.lower() == 'skip': break
            else:
                # 蓄積された過去の指示からQwenが自律延長 [4]
                user_feedback = "AUTOLOOP" 

            # 指示の蓄積
            with open(self.extension_log, "a") as f:
                f.write(json.dumps({"input": user_feedback, "tags": initial_tags}) + "\n")
            
            print(f"🔄 Extending 5s more using: {user_feedback}")
            # Wan 2.2 I2V 実行
            time.sleep(10)

    def run(self):
        print("\n" + "━"*40 + "\n🐺 H-K9 HEAVY OPERATION CENTER: OMEGA\n" + "━"*40)
        while True:
            cmd = input("H-K9 (ID/edit/pose/auto) >> ").strip()
            
            # --- 1. ポーズ・自動化トグル制御 ---
            if cmd == "auto":
                self.automation_on = not self.automation_on
                print(f"🤖 Automation: {self.automation_on}"); continue
            
            # --- 2. Grok型画像編集モード (i2i) [11, 12] ---
            if cmd.startswith("edit"):
                target_img = input("Target Image Path >> ")
                edit_instruction = input("Modification >> ") # 「服を消せ」「資源追加」等
                tags = self._vram_swap_brain(f"Edit {target_img}: {edit_instruction}")
                self.execute_workflow(tags, is_edit=True)
                continue

            # --- 3. 聖典現像シークエンス (58等の数字入力対応) [6] ---
            tags = self.translator.translate(cmd)
            
            # ポーズ指定確認
            pose_choice = input("Pose (none/studio/改) >> ")
            if pose_choice == "studio":
                print("🖱️ [GUI] OpenPose Studio Node active. Click preview in ComfyUI.")
            
            # 静止画現像 -> 自律検品リトライ -> 動画化 -> 延長ループ [4, 9]
            still = self.execute_workflow(tags)
            self.extend_video_loop(still, tags)

if __name__ == "__main__":
    center = HK9CommandCenter()
    center.run()
