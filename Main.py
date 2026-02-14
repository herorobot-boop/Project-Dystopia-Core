# =========================================================
# H-K9 System: Central Command Unit [FINAL INTEGRATION]
# =========================================================
import sys
from pathlib import Path
from core.engines.thought_translator import H_K9_PhysicalSimulator
from core.engines.comfy_api_bridge import ComfyAPIBridge
from core.engines.video_executor import HK9_VideoExecutor
from core.utils.lipsync_handler import HK9_LipSyncHandler

class HK9_CentralCommand:
    def __init__(self):
        print("🏛️ H-K9 System Initializing... [Blackwell Mode Active]")
        self.simulator = H_K9_PhysicalSimulator()
        self.bridge = ComfyAPIBridge()
        self.video_eng = HK9_VideoExecutor()
        self.lipsync = HK9_LipSyncHandler()

    def execute_full_protocol(self, subject_image, scenario_id, modification_id):
        """
        全自動執行プロトコル：
        1. 思想変換 -> 2. LoRA学習&画像現像 -> 3. 音声生成(連携) -> 4. 動画化&LipSync
        """
        print(f"\n[!] Target Scenario: {scenario_id} ({modification_id})")
        
        # 1. 思想・物理演算の翻訳 (Step 4)
        print("[1/4] Translating Holy Scripture into Physics...")
        logic = self.simulator.translate(f"{modification_id} {scenario_id}", intensity=0.95)
        
        # 2. 検体LoRA学習 & 現像 (Step 5)
        # ※実運用時は image_name から LoRA を作成するプロセスを通る
        print("[2/4] Deploying Subject to Giant Factory (JSON Engine)...")
        subject_id = Path(subject_image).stem
        current_render = self.bridge.execute_lora_training(logic, subject_image, f"lora_{subject_id}")
        
        # 3. 音声同期パラメータの計算 (Step 6)
        print("[3/4] Calculating Audio/Physics Coherence...")
        audio_params = self.video_eng.sync_audio_to_physics("資源管理の報告を行います。", intensity=0.95)
        
        # 4. 動画執行 & Lip-Sync (Step 6-B)
        print("[4/4] Finalizing Execution Video with Lip-Sync...")
        final_video = self.lipsync.execute_sync(
            source_image=Path(f"outputs/renders/{subject_id}.png"), 
            audio_file=Path(f"outputs/audio/{subject_id}.wav"),
            output_name=f"FINAL_{subject_id}_{scenario_id}"
        )
        
        print(f"\n[✅] PROTOCOL COMPLETE. Video saved at: {final_video}")

if __name__ == "__main__":
    hk9 = HK9_CentralCommand()
    
    # 実行例：ターゲット画像を指定して「改06 夢の国執行#28」を執行
    hk9.execute_full_protocol(
        subject_image="target_subject_01.jpg", 
        scenario_id="夢の国執行#28", 
        modification_id="改06"
    )
