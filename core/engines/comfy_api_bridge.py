import json
import urllib.request
import urllib.parse
import uuid
import time
from pathlib import Path

# =========================================================
# H-K9 Core: ComfyUI API Bridge v3.5 (Swapping-Compatible)
# =========================================================

class ComfyAPIBridge:
    def __init__(self, server_address="127.0.0.1:8888"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.base_dir = Path(__file__).resolve().parents[2]
        # 23,000行の巨大工場（JSON）の絶対パス
        self.workflow_path = self.base_dir / "config/workflows/wan22_factory_api.json"

    def _find_node_by_title(self, prompt_dict, title):
        """ノードIDが変動しても、ノードに設定した『Title』で住所を特定する安全装置"""
        for node_id, node_info in prompt_dict.items():
            if "_meta" in node_info and node_info["_meta"].get("title") == title:
                return node_id
        return None

    def send_to_factory(self, prompt_text, lora_name="subject_alpha_v3", lora_strength=0.8):
        """設計図を 5090 向けにハックし、API 射出を執行"""
        if not self.workflow_path.exists():
            print(f"❌ [Error] Factory JSON not found at: {self.workflow_path}")
            return None

        # 設計図（ワークフロー）のロード
        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)

        # 1. 重要拠点の動的特定
        # ワークフロー内の CLIPTextEncode (Set_prompt-1) 等を特定
        prompt_node_id = self._find_node_by_title(workflow_data, "Set_prompt-1")
        lora_node_id = self._find_node_by_title(workflow_data, "Set_lora_name")
        
        # フォールバック（タイトルが見つからない場合の既定ID：Ver.3基準）
        if not prompt_node_id: prompt_node_id = "252"
        if not lora_node_id: lora_node_id = "269"

        # 2. パラメータの物理注入
        print(f"💉 [Injection] Writing to Node ID: {prompt_node_id}")
        if prompt_node_id in workflow_data:
            workflow_data[prompt_node_id]["inputs"]["text"] = prompt_text
            
        if lora_node_id in workflow_data:
             # Lora選択と強度の適用
             if "lora_name" in workflow_data[lora_node_id]["inputs"]:
                 workflow_data[lora_node_id]["inputs"]["lora_name"] = f"{lora_name}.safetensors"
             if "strength_model" in workflow_data[lora_node_id]["inputs"]:
                 workflow_data[lora_node_id]["inputs"]["strength_model"] = lora_strength

        # 3. API 射出シークエンス
        payload = {"prompt": workflow_data, "client_id": self.client_id}
        data = json.dumps(payload).encode('utf-8')
        
        url = f"http://{self.server_address}/prompt"
        print(f"🚀 [Launch] Sending to {url}...")
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                prompt_id = result.get('prompt_id')
                print(f"📡 [Confirmed] Genesis Started. Prompt ID: {prompt_id}")
                return prompt_id
        except Exception as e:
            print(f"❌ [API Error] Failed to connect to ComfyUI (Is it running on {self.server_address}?): {e}")
            return None

if __name__ == "__main__":
    # 単体テスト用
    bridge = ComfyAPIBridge()
    test_prompt = "high_viscosity_liquid_coating, anatomical_precision, 8k"
    bridge.send_to_factory(test_prompt, "Dystopia_Subject_01")
