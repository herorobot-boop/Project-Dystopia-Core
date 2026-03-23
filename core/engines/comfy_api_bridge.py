import json
import urllib.request
import uuid
from pathlib import Path

class ComfyAPIBridge:
    def __init__(self, server_address="127.0.0.1:8888"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.base_dir = Path(__file__).resolve().parents[13]
        self.workflow_path = self.base_dir / "config/workflows/wan22_factory_api.json"

    def _find_node_by_title(self, workflow, title):
        """Node IDではなくタイトルで検索する安全機能 [17]"""
        for node_id, node_info in workflow.items():
            if node_info.get("_meta", {}).get("title") == title:
                return node_id
        return None

    def execute_payload(self, positive_prompt, lora_name="subject_alpha"):
        if not self.workflow_path.exists():
            print(f"❌ [Error] Factory JSON missing: {self.workflow_path}")
            return None

        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # 重要拠点の特定と書き換え
        prompt_id = self._find_node_by_title(workflow, "Set_prompt-1") or "252"
        lora_id = self._find_node_by_title(workflow, "Set_lora_name") or "269"

        workflow[prompt_id]["inputs"]["text"] = positive_prompt
        workflow[lora_id]["inputs"]["string"] = lora_name

        # API射出
        p = {"prompt": workflow, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))['prompt_id']
        except Exception as e:
            print(f"❌ [API Error] {e}")
            return None
