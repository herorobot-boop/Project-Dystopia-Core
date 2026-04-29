import os
import sys
import json
import time
import torch
import gc
import multiprocessing
from pathlib import Path
from llama_cpp import Llama

# 内部エンジンのインポート（パスの整合性を確保）
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator
from comfy_api_bridge import ComfyAPIBridge
from ai_inspector import AIInspector
from video_executor import HK9_VideoExecutor

# =========================================================
# 🏛️ Project Dystopia: Final Execution Authority (v3.9 Blackwell Swap)
# =========================================================

class DystopiaIntegratedCommander:
    def __init__(self):
        print("🐺 [H-K9] Operation Center: Omega-Blackwell v3.9 Active.")
        
        # 物理パス設定
        self.base_dir = Path(__file__).resolve().parent
        self.vlm_path = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
        self.dictionary_path = self.base_dir / "config/dictionary/h_k9_dictionary_V2_Final.json"
        self.extension_log = self.base_dir / "logs/video_extension_logic.json"
        
        # エンジン初期化
        self.translator = ThoughtTranslator(dict_path=str(self.dictionary_path))
        self.bridge = ComfyAPIBridge()
        self.inspector = AIInspector()
        self.video = HK9_VideoExecutor()
        
        # 動作トグル
        self.automation_mode = False
        self.pose_enabled = True

        # ログディレクトリの強制確保
        os.makedirs(self.base_dir / "logs", exist_ok=True)

    # 1. 言語ガードレール（除霊機能）
    def _language_guardrail(self, llm_output):
        """AIの自己添削ループを検知し、汚染された記憶を抹殺する"""
        forbidden = ["翻訳", "誤り", "System:", "Assistant:", "修正します"]
        if any(k in llm_output for k in forbidden):
            print("🚨 [Guardrail] 脳のバグ（自己添削ループ）を検知。汚染ログをパージします。")
            if os.path.exists(self.extension_log):
                os.remove(self.extension_log)
            return False  # 再試行トリガー
        return True

    # 2. VRAM完全浄化・思考プロセス（プロセス・スワップ）
    def _run_llm_sub_process(self, prompt, return_dict):
        """子プロセス内で脳を覚醒。終了と同時に32GB VRAMをOSへ強制返還する [1, 5]"""
        try:
            print(f"🧠 [Brain] Blackwell 5090にて深層思考中... (Path: {self.vlm_path})")
            llm = Llama(
                model_path=self.vlm_path,
                n_gpu_layers=-1, # 5090に全レイヤーをオフロード
                n_ctx=4096,
                jinja=True,
                verbose=False
            )
            
            # システムプロンプトの注入：不完全性の現像と物理演算の強調
            response = llm(
                f"<|im_start|>system\nあなたはH-K9執行官です。Do not translate. Describe physical visual details only in English. Emphasis: Squish, Liquid visconsity, CCTV perspective.<|im_end|>\n"
                f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
                max_tokens=512,
                stop=["<|im_end|>"]
            )
            
            output_text = response['choices']['text']
            
            # 脳の完全パージ準備
            del llm
            gc.collect()
            torch.cuda.empty_cache()
            
            # 結果の返却
            return_dict['tags'] = output_text
        except Exception as e:
            print(f"❌ [Error] 思考プロセス障害: {e}")
            return_dict['tags'] = "ERROR_SIGNAL"

    def execute_sequence(self, mission_id):
        """思考 -> 現像 -> 検品 -> 動画化 の全自動執行ループ [6, 7]"""
        print(f"\n" + "═"*60 + f"\n🚀 MISSION START: {mission_id}\n" + "═"*60)

        # --- PHASE 1: 脳の覚醒 (Swap Protocol) ---
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        
        # 聖典から基本情報を抽出
        raw_detail = self.translator.translate(mission_id)
        
        p = multiprocessing.Process(target=self._run_llm_sub_process, args=(raw_detail, return_dict))
        p.start()
        p.join() # 思考完了を待機
        
        # この時点で子プロセスが消滅し、VRAMは「完全に空」になる
        refined_tags = return_dict.get('tags', "")

        if refined_tags == "ERROR_SIGNAL" or not self._language_guardrail(refined_tags):
            print("🔄 [Retry] システムを再起動し、再試行します...")
            return self.execute_sequence(mission_id)

        print(f"✨ [Thought] Refined Tags: {refined_tags[:100]}...")
        print("🧹 [VRAM] Brain purged. 32GB Territory is now Open for Wan 2.2.")
        time.sleep(1.5) # ドライバレベルの解放待機 [8]

        # --- PHASE 2: 肉体の現像 (ComfyUI API) ---
        print("🎨 [Still] Rendering High-Precision Image (Z-Image)...")
        still_asset = self.bridge.generate(refined_tags)
        
        # --- PHASE 3: 自律検品 (Qwen2-VL) ---
        is_passed, report = self.inspector.inspect(still_asset, mission_id)
        print(f"🧐 [Inspect] {report}")

        if not is_passed:
            print("⚠️ [Quality Alert] 基準未達。再射出を準備します。")
            return self.execute_sequence(mission_id)

        # --- PHASE 4: 動画化リレー (Wan 2.2) ---
        print("🎬 [Video] Converting Still to Motion (Wan 2.2 I2V)...")
        video_asset = self.video.execute_video_generation(still_asset, refined_tags)
        
        print(f"\n[📦] FINAL ARCHIVE COMPLETE: {video_asset}")

    def run(self):
        print("\n" + "█"*60)
        print("      H-K9 OMEGA COMMAND CENTER: 5090 BLACKWELL EDITION")
        print("      MODE: PROCESS SWAP / LANGUAGE GUARDRAIL ENABLED")
        print("█"*60 + "\n")

        while True:
            try:
                cmd = input("H-K9 (ID/edit/pose_toggle/auto_toggle) >> ").strip()
                
                if cmd.lower() in ["exit", "quit"]: break
                if cmd == "auto_toggle":
                    self.automation_mode = not self.automation_mode
                    print(f"🤖 Automation Mode: {self.automation_mode}"); continue
                if cmd == "pose_toggle":
                    self.pose_enabled = not self.pose_enabled
                    print(f"🦴 Pose Control: {self.pose_enabled}"); continue

                if cmd.startswith("V2_"):
                    self.execute_sequence(cmd)
                else:
                    print("⚠️ [Access Denied] 聖典ID（V2_XXX）を入力してください。")
            
            except KeyboardInterrupt:
                print("\n👋 [Termination] Sequence interrupted. Cooling down Blackwell...")
                break

if __name__ == "__main__":
    commander = DystopiaIntegratedCommander()
    commander.run()
