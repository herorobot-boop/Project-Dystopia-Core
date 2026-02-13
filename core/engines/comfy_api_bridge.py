# =========================================================
# H-K9 Core: ComfyUI API Bridge [Step 5 最終執行版]
# =========================================================
import json
import requests
import uuid
from pathlib import Path

class ComfyAPIBridge:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        # あなたが保存した23000行のJSONのパス
        self.workflow_path = Path("/workspace/Project-Dystopia-Core/config/workflows/hk9_lora_train_base.json")

    def _load_workflow(self):
        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def execute_lora_training(self, prompt_data, image_name, lora_name):
        """
        巨大なワークフローJSONの特定NodeにH-K9のデータを注入し、APIへ射出する
        """
        # 解析済みのNode ID
        NODE_PROMPT = "252"      # Set_prompt-1 (STRING)
        NODE_IMAGE = "271"       # Load Image (image)
        NODE_LORA_NAME = "269"   # Set_lora_name (STRING)

        workflow = self._load_workflow()
        
        # 1. 聖典の物理演算プロンプトを注入
        # prompt_data["positive"] には '改06' などの結果が入っている
        workflow["nodes"] = self._update_node_value(workflow["nodes"], NODE_PROMPT, prompt_data["positive"])
        
        # 2. 検体画像のファイル名を指定
        workflow["nodes"] = self._update_node_value(workflow["nodes"], NODE_IMAGE, image_name)
        
        # 3. 生成されるLoRAの名前を指定
        workflow["nodes"] = self._update_node_value(workflow["nodes"], NODE_LORA_NAME, lora_name)

        # API射出
        payload = {"prompt": workflow, "client_id": self.client_id}
        
        print(f"[*] H-K9 Gateway: Dispatching Subject Capture Protocol...")
        print(f"[*] Target: {lora_name} | Logic: {prompt_data['positive'][:50]}...")
        
        try:
            response = requests.post(f"http://{self.server_address}/prompt", json=payload)
            return response.json()
        except Exception as e:
            print(f"[ERROR] API Connection Failed: {e}")
            return None

    def _update_node_value(self, nodes, node_id, value):
        """指定したIDのノードの値を書き換える"""
        for node in nodes:
            if str(node["id"]) == node_id:
                # ComfyUIのAPI形式に合わせてwidgets_valuesを更新
                if "widgets_values" in node:
                    node["widgets_values"][0] = value
        return nodes

if __name__ == "__main__":
    # 動作テスト
    from thought_translator import H_K9_PhysicalSimulator
    sim = H_K9_PhysicalSimulator()
    bridge = ComfyAPIBridge()
    
    # 指令：改06（資源コーティング）
    logic = sim.translate("改06 夢の国執行#28", intensity=0.9)
    
    # 執行（APIへ送信）
    bridge.execute_lora_training(logic, "target_girl.jpg", "subject_alpha_lora")
