# =========================================================
# H-K9 Core: ComfyUI API Bridge [Step 5 執行]
# =========================================================
import json
import requests
import websocket # websocket-client
import uuid
from pathlib import Path

class ComfyAPIBridge:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.workflow_path = Path("/workspace/Project-Dystopia-Core/config/workflows/hk9_lora_train_base.json")

    def _load_workflow(self):
        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def inject_and_execute(self, prompt_data, lora_name=None):
        """
        ThoughtTranslatorからの物理演算出力をComfyUIワークフローに注入
        """
        workflow = self._load_workflow()
        
        # 1. 物理演算プロンプトの注入（IDはワークフローに依存するため要調整）
        # 例: Node ID '6' が CLIP Text Encode だと仮定
        workflow["6"]["inputs"]["text"] = prompt_data["positive"]
        
        # 2. 自動生成された検体LoRAの適用
        if lora_name:
            # LoRA Loaderノードへの動的注入
            workflow["10"]["inputs"]["lora_name"] = f"subjects/{lora_name}.safetensors"
            workflow["10"]["inputs"]["strength_model"] = 0.85

        # 3. 光学ハック（Denoise値）の同期
        workflow["3"]["inputs"]["denoise"] = prompt_data["denoise"]

        # 4. API射出
        p = {"prompt": workflow, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        
        print(f"[*] Dispatching Payload to ComfyUI Engine... (Target: {lora_name if lora_name else 'Base'})")
        response = requests.post(f"http://{self.server_address}/prompt", data=data)
        return response.json()

# --- 統合テスト ---
if __name__ == "__main__":
    # Step 4のエンジンから出力を受け取る想定
    from thought_translator import H_K9_PhysicalSimulator
    
    sim = H_K9_PhysicalSimulator()
    bridge = ComfyAPIBridge()
    
    # 指令：改06 夢の国執行#28
    payload = sim.translate("改06 夢の国執行#28", intensity=0.95)
    
    # 執行：検体'subject_alpha'として現像
    bridge.inject_and_execute(payload, lora_name="subject_alpha")
