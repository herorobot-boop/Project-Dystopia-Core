import json
import urllib.request
import uuid
import time
from pathlib import Path

class ComfyAPIBridge:
    def __init__(self, server_address="127.0.0.1:8888"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.base_dir = Path(__file__).resolve().parents[2]
        self.workflow_path = self.base_dir / "config/workflows/wan22_factory_api.json"

    def _find_node_by_title(self, workflow, title):
        """Node ID 変動を吸収するタイトル検索エンジン"""
        for node_id, node_info in workflow.items():
            if "_meta" in node_info and node_info["_meta"].get("title") == title:
                return node_id
        return None

    def execute_payload(self, positive_prompt, lora_name="subject_alpha_v3"):
        if not self.workflow_path.exists():
            print(f"❌ [Error] Workflow JSON missing: {self.workflow_path}")
            return None

        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # 5090 Blackwell 向けインジェクション
        prompt_id = self._find_node_by_title(workflow, "Set_prompt-1") or "252"
        lora_id = self._find_node_by_title(workflow, "Set_lora_name") or "269"

        workflow[prompt_id]["inputs"]["text"] = positive_prompt
        if "lora_name" in workflow[lora_id]["inputs"]:
            workflow[lora_id]["inputs"]["lora_name"] = f"{lora_name}.safetensors"

        payload = {"prompt": workflow, "client_id": self.client_id}
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        req.add_header('Content-Type', 'application/json')

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))['prompt_id']
        except Exception as e:
            print(f"❌ [API Error] Connection to Factory failed: {e}")
            return None
