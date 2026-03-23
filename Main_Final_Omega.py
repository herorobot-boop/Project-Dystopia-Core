import os
import sys
import time
import torch
import gc
from pathlib import Path

# 各種エンジンのパスを通す
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator
from comfy_api_bridge import ComfyAPIBridge
from ai_inspector import AIInspector
from video_executor import VideoExecutor

# =========================================================
# 🏛️ Project Dystopia: The Final Omega Command (Ver.3.5.1)
# =========================================================

class DystopiaCommander:
    def __init__(self):
        print("🐺 [H-K9] Final Authority: Active.")
        self.translator = ThoughtTranslator()
        self.bridge = ComfyAPIBridge()
        self.inspector = AIInspector()
        self.video = VideoExecutor()
        
        # 物理ディレクトリの定義
        self.output_dir = Path("/workspace/ComfyUI/output")
        self.success_dir = Path("/workspace/Dystopia_Final_Assets")
        self.success_dir.mkdir(parents=True, exist_ok=True)

    def _wait_for_file(self, prompt_id, timeout=180):
        """ComfyUI からのファイル着弾を物理監視"""
        start_time = time.time()
        print(f"⏳ [Wait] Monitoring factory output for Prompt ID: {prompt_id}...")
        while time.time() - start_time < timeout:
            # 最新のPNGファイルをスキャン
            files = sorted(self.output_dir.glob("*.png"), key=os.path.getmtime)
            if files:
                latest = files[-1]
                # 書き込み完了を待機（1秒間サイズ変化なしを確認）
                size_before = latest.stat().st_size
                time.sleep(1.5)
                if latest.stat().st_size == size_before and size_before > 0:
                    return latest
            time.sleep(3)
        return None

    def execute_sequence(self, mission_id):
        print(f"\n" + "═"*60)
        print(f"🚀 [H-K9] 執行開始: {mission_id}")
        print("═"*60)

        # --- PHASE 1: 脳の覚醒 (Thought Translator) ---
        # Note: ThoughtTranslator 内部で Llama を呼ぶよう構成済み
        print("🧠 [Phase 1] Thinking...")
        from thought_translator import HK9Brain # 交互覚醒用ラッパー
        brain = HK9Brain() 
        physics_tags = brain.generate_high_density_tags(mission_id)
        del brain
        gc.collect()
        torch.cuda.empty_cache()

        # --- PHASE 2: 静止画現像 & 検品ループ (Still Rendering & Audit) ---
        success_image = None
        for attempt in range(1, 4):
            print(f"\n🎨 [Phase 2] Rendering Attempt {attempt}/3...")
            prompt_id = self.bridge.execute_payload(physics_tags)
            
            output_path = self._wait_for_file(prompt_id)
            if not output_path:
                print("❌ [Timeout] Factory failed to respond.")
                continue

            # --- PHASE 3: 自律検品 (AI Inspector) ---
            print("🧐 [Phase 3] AI Inspection (Qwen2-VL)...")
            passed, audit_msg = self.inspector.inspect(output_path, mission_id)
            print(f"📊 {audit_msg}")

            if passed:
                success_image = output_path
                print("✅ [AESTHETIC PASSED] Moving to Video Synthesis.")
                break
            else:
                print("♻️ [REJECTED] Quality below threshold. Re-shooting...")
                # 失敗作をリネームして隔離
                output_path.rename(output_path.with_suffix(".rejected"))

        if not success_image:
            print("💀 [TERMINATED] Failed to reach quality standards.")
            return

        # --- PHASE 4: 動画化 (Wan 2.2 Video Synthesis) ---
        print("\n🎬 [Phase 4] Transitioning to Motion Synthesis (Wan 2.2)...")
        video_prompt_id = self.video.execute_video_generation(success_image, physics_tags)
        
        if video_prompt_id:
            print(f"🏁 [Final] Mission Accomplished. Video Dispatch ID: {video_prompt_id}")
            print(f"📂 [Asset] Master image stored at: {success_image}")
        else:
            print("❌ [Video Failure] Motion synthesis engine crashed.")

    def run_command_center(self):
        print("\n" + "█"*60)
        print("      H-K9 HEAVY OPERATION CENTER: OMEGA-BLACKWELL V3.5.1")
        print("      STATUS: READY FOR MASS LOGISTICS AUDIT")
        print("█"*60)

        while True:
            try:
                cmd = input("\nH-K9 >> ").strip()
                if not cmd: continue
                if cmd.lower() in ["exit", "quit"]: break
                
                if cmd.startswith("V2_"):
                    self.execute_sequence(cmd)
                else:
                    print("⚠️ [Wait] 合言葉は 'V2_' で開始してください。")
            except KeyboardInterrupt:
                print("\n👋 [Termination] Sequence interrupted.")
                break

if __name__ == "__main__":
    commander = DystopiaCommander()
    commander.run_command_center()
