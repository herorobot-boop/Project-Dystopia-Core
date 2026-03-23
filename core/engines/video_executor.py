import json
import urllib.request
from pathlib import Path

class VideoExecutor:
    def __init__(self, server_address="127.0.0.1:8888"):
        self.server_address = server_address
        self.base_dir = Path(__file__).resolve().parents[2]
        # 動画用ワークフロー（23,000行の別設計図）
        self.video_workflow_path = self.base_dir / "config/workflows/wan22_video_factory.json"

    def execute_video_generation(self, image_path, physics_tags):
        """静止画を起点に、Blackwell 5090 で 5秒間の物理シミュレーション動画を生成"""
        if not self.video_workflow_path.exists():
            print("❌ [Error] Video Workflow JSON missing.")
            return None

        with open(self.video_workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # ノード特定と注入（Image-to-Video プロトコル）
        # 静止画パス、プロンプト、モーション強度を同期
        for node_id, node in workflow.items():
            title = node.get("_meta", {}).get("title", "")
            if title == "Load_Source_Image":
                node["inputs"]["image"] = image_path
            elif title == "Set_Video_Prompt":
                node["inputs"]["text"] = f"{physics_tags}, fluid simulation, high dynamic motion"

        payload = {"prompt": workflow}
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['prompt_id']
        except Exception as e:
            print(f"❌ [Video Error] {e}")
            return None
