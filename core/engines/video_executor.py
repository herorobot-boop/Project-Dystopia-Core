import json
import requests
from pathlib import Path

# =========================================================
# H-K9 Core: Video Executor v3.5 (Wan 2.2 I2V Control)
# =========================================================

class VideoExecutor:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.base_dir = Path(__file__).resolve().parents[1]
        self.workflow_path = self.base_dir / "config/workflows/wan22_motion_api.json"

    def execute_video_generation(self, still_image_path, motion_tags):
        """静止画を Wan 2.2 に流し込み動画化"""
        if not self.workflow_path.exists():
            print(f"❌ [Error] Video Factory JSON not found.")
            return None

        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # 静止画パスとモーションプロンプトの注入
        # IDは wan22_factory_api.json の定義に準拠
        workflow["154"]["inputs"]["image"] = str(still_image_path)
        workflow["155"]["inputs"]["text"] = f"{motion_tags}, 24fps, high-fidelity motion, fluid interaction"

        print(f"🚀 [Motion] Dispatching to Wan 2.2 Engine...")
        p = {"prompt": workflow}
        data = json.dumps(p).encode('utf-8')
        req = requests.post(f"http://{self.server_address}/prompt", data=data)
        
        return req.json().get("prompt_id")

if __name__ == "__main__":
    executor = VideoExecutor()
    executor.execute_video_generation("output.png", "rhythmic pelvic thrusting, liquid splashing")
