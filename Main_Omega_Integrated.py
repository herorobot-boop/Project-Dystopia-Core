import os
import sys
import time
import torch
import gc
import json
import requests
from pathlib import Path
from llama_cpp import Llama

# 内部エンジンのインポート（パスの整合性を確保）
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator
from comfy_api_bridge import ComfyAPIBridge
from ai_inspector import AIInspector
from video_executor import VideoExecutor

# =========================================================
# 🏛️ Project Dystopia: Final Execution Authority (Omega-Blackwell)
# =========================================================

class DystopiaProjectManager:
    def __init__(self):
        print("🐺 [H-K9] Operation Center: Level 5 Authority Active.")
        self.translator = ThoughtTranslator()
        self.bridge = ComfyAPIBridge()
        self.inspector = AIInspector()
        self.video = VideoExecutor()
        
        # モデルパスの物理固定
        self.vlm_path = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
        self.output_dir = Path("/workspace/ComfyUI/output")

    def _swap_awaken_brain(self, script_id):
        """【交互覚醒：思考】LLMを召喚し、翻訳後にVRAMを強制浄化"""
        print(f"\n🧠 [Thought] Awakening Qwen 3.5 IQ4_XS: {script_id}")
        
        # 5090に最適化されたロード
        llm = Llama(
            model_path=self.vlm_path,
            n_gpu_layers=-1,
            n_ctx=4096,
            jinja=True,
            verbose=False
        )

        # 聖典V2の解釈と物理演算タグへの翻訳
        raw_translation = self.translator.translate(script_id)
        
        # 高密度化推論
        prompt = f"USER: Expand this into high-density physics tags for Blackwell 5090: {raw_translation}\nASSISTANT:"
        output = llm(prompt, max_tokens=1024)
        tags = output['choices'][0]['text']

        # 【最重要】脳の完全排除
        del llm
        gc.collect()
        time.sleep(1) # VRAM解放の物理待機
        torch.cuda.empty_cache()
        print("🧹 [VRAM] Brain purged. 32GB Territory is now Open.")
        return tags

    def wait_for_output(self, mission_id, timeout=120):
        """物理ファイルの着弾をポーリング監視（WebSocketの代替）"""
        start_time = time.time()
        print(f"⏳ [Wait] Waiting for factory output: {mission_id}...")
        while time.time() - start_time < timeout:
            # ComfyUIの出力ファイル命名規則に合わせて検索
            files = list(self.output_dir.glob(f"*{mission_id}*.png"))
            if files:
                return sorted(files, key=os.path.getmtime)[-1]
            time.sleep(2)
        return None

    def execute_full_cycle(self, mission_id):
        """思考 -> 現像 -> 検品 -> 動画化 の全自動執行ループ"""
        print(f"\n━━━━━━━━━━━━ Mission Start: {mission_id} ━━━━━━━━━━━━")

        # 1. 思考フェーズ
        physics_tags = self._swap_awaken_brain(mission_id)

        # 2. 静止画現像フェーズ (Retryループ)
        success_image = None
        for attempt in range(3): # 最大3回まで自律リトライ
            print(f"🎨 [Phase 2] Rendering Still (Attempt {attempt+1}/3)...")
            prompt_id = self.bridge.send_to_factory(physics_tags)
            
            # 生成完了待機
            output_path = self.wait_for_output(mission_id)
            if not output_path:
                print("❌ [Error] Factory Timeout. Retrying...")
                continue

            # 3. 自律検品フェーズ (AI Inspector)
            print("🧐 [Phase 3] AI Inspection (Qwen2-VL)...")
            passed, msg = self.inspector.inspect(output_path, mission_id)
            print(msg)

            if passed:
                success_image = output_path
                break
            else:
                print(f"♻️ [Retry] Aesthetic failure. Re-adjusting weights and re-shooting...")
                time.sleep(2)

        if not success_image:
            print("💀 [Abort] Mission failed after 3 attempts. Insufficient quality.")
            return

        # 4. 動画化フェーズ (Wan 2.2)
        print("🎬 [Phase 4] Transitioning to Motion Synthesis (Wan 2.2)...")
        video_id = self.video.execute_video_generation(str(success_image), physics_tags)
        
        print(f"🏁 [Final] Mission Accomplished. Video ID: {video_id}")
        print(f"📂 [Storage] Target safely stored at: {success_image}")

if __name__ == "__main__":
    commander = DystopiaProjectManager()
    print("\n" + "═"*50)
    print("🐺 H-K9 HEAVY OPERATION CENTER: OMEGA-BLACKWELL V3.5.1")
    print("═"*50)

    while True:
        try:
            mission = input("\nH-K9 >> ").strip()
            if not mission: continue
            if mission.lower() in ["exit", "quit"]: break
            
            if mission.startswith("V2_"):
                commander.execute_full_cycle(mission)
            else:
                print("⚠️ [Access Denied] Mission ID must start with 'V2_'.")
        except KeyboardInterrupt:
            print("\n👋 [Termination] Sequence interrupted by Commander.")
            break
