import json
import urllib.request
import os
from pathlib import Path

# =========================================================
# H-K9 Core: Video Executor v1.1 (Wan 2.2 Turbo Control)
# =========================================================

class VideoExecutor:
    def __init__(self, server_address="127.0.0.1:8888"):
        self.server_address = server_address
        self.base_dir = Path(__file__).resolve().parents[2]
        self.video_workflow_path = self.base_dir / "config/workflows/wan22_video_factory.json"

    def execute_video_generation(self, image_path, physics_tags):
        """合格した静止画を Wan 2.2 エンジンへ射出し、動画化を執行"""
        if not self.video_workflow_path.exists():
            print("❌ [Error] Video Factory Workflow (JSON) missing.")
            return None

        with open(self.video_workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # 5090 Blackwell 最適化：I2V ノードへの物理インジェクション
        # ComfyUIのノードタイトルで動的に検索
        for node_id, node in workflow.items():
            title = node.get("_meta", {}).get("title", "")
            
            # 静止画ソースの注入
            if title == "Load_Source_Image":
                # ファイル名のみではなく、絶対パスが通るよう処理
                node["inputs"]["image"] = str(image_path)
            
            # 物理タグとモーションの注入
            elif title == "Set_Video_Prompt":
                node["inputs"]["text"] = (
                    f"{physics_tags}, fluid dynamic interaction, high fidelity, "
                    "rhythmic motion, extremely detailed textures, 4k resolution"
                )
            
            # モーション強度の制御（オプション）
            elif title == "Motion_Control":
                node["inputs"]["strength"] = 1.2

        payload = {"prompt": workflow}
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        req.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                prompt_id = result['prompt_id']
                print(f"🎬 [Video] Dispatch successful. Factory ID: {prompt_id}")
                return prompt_id
        except Exception as e:
            print(f"❌ [Video Error] Factory connection failed: {e}")
            return None

if __name__ == "__main__":
    executor = VideoExecutor()
    # executor.execute_video_generation("/workspace/output/success.png", "splashing fluid, tissue displacement")
