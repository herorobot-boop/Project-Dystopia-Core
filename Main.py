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
        self.bridge = ComfyAPIBridge(server_address="127.0.0.1:8888")
        self.inspector = AIInspector()
        self.video = VideoExecutor()
        
        # モデルパスと出力先の物理固定
        self.vlm_path = "/workspace/models/vlm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
        self.output_dir = Path("/workspace/ComfyUI/output")

    def _swap_awaken_brain(self, script_id):
        """【交互覚醒：思考】LLMを召喚し、翻訳後にVRAMを強制浄化"""
        print(f"\n🧠 [Thought] Awakening Qwen 3.5 IQ4_XS for Mission: {script_id}")
        
        # 5090の32GBを一時的に占有
        llm = Llama(
            model_path=self.vlm_path,
            n_gpu_layers=-1,
            n_ctx=4096,
            jinja=True,
            verbose=False
        )

        # 聖典V2の解釈と物理演算タグへの翻訳
        raw_translation = self.translator.translate(script_id)
        
        # Blackwellの高密度演算を活用したタグ拡張
        prompt = f"USER: Expand this into high-density physics and anatomical tags for Blackwell 5090: {raw_translation}\nASSISTANT:"
        output = llm(prompt, max_tokens=1024)
        tags = output['choices'][0]['text']

        # 【最重要】脳の完全排除：Wan 2.2のために領土を空ける
        del llm
        gc.collect()
        time.sleep(1.5) # ドライバレベルのVRAM解放を待機
        torch.cuda.empty_cache()
        print("🧹 [VRAM] Brain purged. 32GB Territory is now Open for Factory.")
        return tags

    def wait_for_output(self, mission_id, timeout=300):
        """物理ファイルの着弾をポーリング監視（非同期エラーを抹殺）"""
        start_time = time.time()
        print(f"⏳ [Wait] Monitoring factory output for Mission ID: {mission_id}...")
        
        while time.time() - start_time < timeout:
            # ComfyUIの出力ファイルにMission IDが含まれているか、最新ファイルをチェック
            # ファイル名はワークフロー側の設定に依存するため、最新のPNGを取得
            files = list(self.output_dir.glob("*.png"))
            if files:
                latest_file = sorted(files, key=os.path.getmtime)[-1]
                # ファイルが書き込み中（ロック）でないか簡易チェック
                prev_size = latest_file.stat().st_size
                time.sleep(1)
                if latest_file.stat().st_size == prev_size and prev_size > 0:
                    return latest_file
            time.sleep(3)
        return None

    def execute_full_cycle(self, mission_id):
        """思考 -> 現像 -> 検品 -> 動画化 の全自動執行ループ"""
        print(f"\n" + "═"*60)
        print(f"🚀 MISSION START: {mission_id}")
        print("═"*60)

        # 1. 思考フェーズ (VRAM: LLM占有)
        physics_tags = self._swap_awaken_brain(mission_id)

        # 2. 静止画現像フェーズ (VRAM: ComfyUI占有 / Retryループ)
        success_image = None
        for attempt in range(3): 
            print(f"\n🎨 [Phase 2] Rendering (Attempt {attempt+1}/3)...")
            prompt_id = self.bridge.send_to_factory(physics_tags)
            
            # 物理的着弾待機
            output_path = self.wait_for_output(mission_id)
            if not output_path:
                print("❌ [Timeout] Factory failed to produce output. Retrying...")
                continue

            # 3. 自律検品フェーズ (VRAM: Inspector占有)
            print("🧐 [Phase 3] AI Inspection (Qwen2-VL)...")
            passed, score_msg = self.inspector.inspect(output_path, mission_id)
            print(f"📊 [Score] {score_msg}")

            if passed:
                success_image = output_path
                print("✅ [AESTHETIC PASSED] Quality standards met.")
                break
            else:
                print(f"♻️ [REJECTED] SQUISH score insufficient. Re-calculating parameters...")
                # ファイルをリネームしてバックアップし、再試行
                output_path.rename(output_path.with_suffix(".failed"))
                time.sleep(2)

        if not success_image:
            print("💀 [TERMINATED] Mission failed after 3 attempts. Resource allocation aborted.")
            return

        # 4. 動画化フェーズ (Wan 2.2 Turbo)
        print("\n🎬 [Phase 4] Transitioning to Motion Synthesis (Wan 2.2)...")
        video_id = self.video.execute_video_generation(str(success_image), physics_tags)
        
        print(f"\n" + "═"*60)
        print(f"🏁 MISSION ACCOMPLISHED: {mission_id}")
        print(f"📂 FINAL PRODUCT: {success_image}")
        print(f"🎬 VIDEO ID: {video_id}")
        print("═"*60)

if __name__ == "__main__":
    commander = DystopiaProjectManager()
    
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
                commander.execute_full_cycle(mission)
            else:
                print("⚠️ [Access Denied] Mission ID must start with 'V2_'.")
        except KeyboardInterrupt:
            print("\n👋 [Termination] Sequence interrupted. Cooling down Blackwell 5090...")
            break
