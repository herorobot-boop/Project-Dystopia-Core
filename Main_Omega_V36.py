import sys
import torch
import gc
from pathlib import Path

# 既存エンジン群
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator
from comfy_api_bridge import ComfyAPIBridge
from ai_inspector import AIInspector # Qwen3-VL 統合版
from video_executor import VideoExecutor

class DystopiaIntegratedCommander:
    def __init__(self):
        self.translator = ThoughtTranslator() # Qwen3.5-Uncensored 駆動
        self.bridge = ComfyAPIBridge()
        self.inspector = AIInspector()
        self.video = VideoExecutor()

    def execute_full_cycle(self, mission_id):
        """15分無双：思考 ➡ 現像 ➡ 検品 ➡ 動画化 のシリアル処理"""
        
        # Phase 1: 思考 (Uncensored Brain)
        # 規制のない高密度物理タグを生成
        physics_tags = self.translator.translate(mission_id)
        self._purge_vram()

        # Phase 2: 静止画現像 & 検品
        success_image = None
        for i in range(3):
            print(f"🎨 Rendering Still Image (Attempt {i+1})...")
            prompt_id = self.bridge.execute_payload(physics_tags)
            image_path = self._wait_for_output(prompt_id)
            
            # Phase 3: 自律検品 (Qwen3-VL)
            passed, report = self.inspector.inspect(image_path, mission_id)
            print(f"📊 Audit: {report}")
            
            if passed:
                success_image = image_path
                break
            self._purge_vram()

        # Phase 4: 動画化 (Wan 2.2 Turbo)
        if success_image:
            print("🎬 Image Passed. Launching Video Synthesis (Wan 2.2)...")
            video_id = self.video.execute_video_generation(success_image, physics_tags)
            print(f"✅ Mission Success. Video Prompt ID: {video_id}")

    def _purge_vram(self):
        """交互覚醒の鉄則：Blackwell 32GB を完全に明け渡す"""
        gc.collect()
        torch.cuda.empty_cache()

# --- [図解：交互覚醒パイプライン] ---
#
