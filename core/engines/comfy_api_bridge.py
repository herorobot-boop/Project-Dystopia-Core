# =========================================================
# H-K9 Core: ComfyUI API Bridge [v7.2 Headless Edition]
# =========================================================
import json
import requests
from pathlib import Path

class ComfyAPIBridge:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.workflow_path = Path("/workspace/Project-Dystopia-Core/config/workflows/hk9_lora_train_base.json")

    def _get_node_by_title(self, workflow, title):
        """ノードのタイトルから対象を探し、その辞書オブジェクトを返す"""
        for node in workflow.get("nodes", []):
            if node.get("title") == title:
                return node
        return None

    def execute(self, prompt_text, image_filename, lora_name):
        """
        JSONを読み込み、値を注入してAPIへPOST送信する
        """
        if not self.workflow_path.exists():
            print(f"[ERROR] Workflow JSON not found: {self.workflow_path}")
            return None

        # 1. 設計図（巨大JSON）のロード
        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # 2. 値の注入（タイトルベースで特定）
        # 物理演算プロンプト
        prompt_node = self._get_node_by_title(workflow, "Set_prompt-1")
        if prompt_node:
            prompt_node["widgets_values"] = [prompt_text]

        # 検体画像
        image_node = self._get_node_by_title(workflow, "Load Image")
        if image_node:
            image_node["widgets_values"] = [image_filename]

        # 保存名
        name_node = self._get_node_by_title(workflow, "Set_lora_name")
        if name_node:
            name_node["widgets_values"] = [lora_name]

        # 3. API射出
        print(f"[*] H-K9 API Bridge: Dispatching to {self.server_address}...")
        payload = {"prompt": workflow}
        
        try:
            response = requests.post(
                f"http://{self.server_address}/prompt", 
                json=payload
            )
            if response.status_code == 200:
                print(f"[✅] Success: Prompt queued. ID: {response.json().get('prompt_id')}")
                return response.json()
            else:
                print(f"[❌] API Error: {response.text}")
                return None
        except Exception as e:
            print(f"[❌] Connection Failed: {e}")
            return None

if __name__ == "__main__":
    # 単体テスト用
    bridge = ComfyAPIBridge()
    bridge.execute("改06 夢の国執行#28 test", "target.jpg", "subject_alpha_lora")
