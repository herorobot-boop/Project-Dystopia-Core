import os
import sys
import time
import torch
import gc
import shutil
from pathlib import Path

# 既存エンジン群のパス解決
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator
from comfy_api_bridge import ComfyAPIBridge
from ai_inspector import AIInspector
from video_executor import VideoExecutor

class DystopiaIntegratedCommander:
    def __init__(self):
        print("🐺 [H-K9] Integrated Commander V3.6: Initializing...")
        self.translator = ThoughtTranslator() # Uncensored駆動
        self.bridge = ComfyAPIBridge()
        self.inspector = AIInspector()
        self.video = VideoExecutor()
        self.output_dir = Path("/workspace/ComfyUI/output")

    def _wait_for_output(self, prompt_id, timeout=300):
        """ComfyUIからのファイル着弾を物理監視（300秒タイムアウト）"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            files = sorted(self.output_dir.glob("*.png"), key=os.path.getmtime)
            if files:
                latest = files[-1]
                # 書き込み完了を待機
                size_before = latest.stat().st_size
                time.sleep(2.0)
                if latest.stat().st_size == size_before:
                    return latest
            time.sleep(3)
        return None

    def execute_full_cycle(self, mission_id):
        """思考 ➡ 現像 ➡ 検品 ➡ 動画化 のシリアル処理"""
        print(f"\n🚀 [H-K9] 執行開始: {mission_id}")
        
        # Phase 1: 思考 (Uncensored Brain)
        physics_tags = self.translator.translate(mission_id)
        self._purge_vram()

        # Phase 2: 静止画現像 & 検品 (Attempt 3回)
        success_image = None
        for i in range(3):
            print(f"🎨 Rendering Still Image (Attempt {i+1}/3)...")
            prompt_id = self.bridge.execute_payload(physics_tags)
            image_path = self._wait_for_output(prompt_id)
            
            if not image_path:
                print("⚠️ [Timeout] Image generation failed.")
                continue

            # Phase 3: 自律検品 (Qwen2.5-VL)
            passed, report = self.inspector.inspect(image_path, mission_id)
            print(f"📊 Audit Report: {report}")
            
            if passed:
                success_image = image_path
                # 傑作として隔離保存
                dest = Path("/workspace/Dystopia_Final_Assets") / f"PASS_{mission_id}_{int(time.time())}.png"
                dest.parent.mkdir(exist_ok=True)
                shutil.copy(image_path, dest)
                break
            
            self._purge_vram()

        # Phase 4: 動画化 (Wan 2.2 Turbo)
        if success_image:
            print("🎬 [Success] Launching Video Synthesis (Wan 2.2 Turbo)...")
            video_id = self.video.execute_video_generation(success_image, physics_tags)
            print(f"✅ Mission Accomplished. Video Prompt ID: {video_id}")
        else:
            print("💀 [Failed] Quality standards not met. Sequence terminated.")

    def _purge_vram(self):
        """Blackwell 32GB を完全に明け渡す"""
        gc.collect()
        torch.cuda.empty_cache()
        time.sleep(1.5)

if __name__ == "__main__":
    commander = DystopiaIntegratedCommander()
    # 実行例: commander.execute_full_cycle("V2_執行ログ#151_1")
