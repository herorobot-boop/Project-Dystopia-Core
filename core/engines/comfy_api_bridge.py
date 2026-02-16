# =========================================================
# H-K9 Core: ComfyUI API Bridge [v7.3 Final Accuracy]
# =========================================================
import json
import requests
from pathlib import Path

class ComfyAPIBridge:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.workflow_path = Path("/workspace/Project-Dystopia-Core/config/workflows/hk9_lora_train_base.json")

    def execute(self, prompt_text, image_filename, lora_name):
        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # NotebookLMにより特定された物理IDへの直接注入
        # ID 252: Prompt, ID 271: Load Image, ID 269: LoRA Name
        workflow["nodes"] = self._update_node(workflow["nodes"], 252, [prompt_text])
        workflow["nodes"] = self._update_node(workflow["nodes"], 271, [image_filename])
        workflow["nodes"] = self._update_node(workflow["nodes"], 269, [lora_name])

        print(f"[*] H-K9 API Bridge: Dispatching to ID 252, 271, 269...")
        payload = {"prompt": workflow}
        
        try:
            response = requests.post(f"http://{self.server_address}/prompt", json=payload)
            return response.json()
        except Exception as e:
            print(f"[❌] Dispatch Failed: {e}")
            return None

    def _update_node(self, nodes, node_id, values):
        for node in nodes:
            if node.get("id") == node_id:
                node["widgets_values"] = values
                break
        return nodes
