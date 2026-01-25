import json
import sys
from pathlib import Path

# --- 神経接続：プロジェクトルートの特定 ---
BASE_DIR = Path(__file__).resolve().parents[1]

class WorkflowMapper:
    def __init__(self, template_name="Chronos_V3_Workflow.json"):
        """
        workflows/ フォルダからテンプレートを自動ロードする。
        """
        self.template_path = BASE_DIR / "workflows" / template_name
        self.template = self._load_template()

    def _load_template(self):
        if not self.template_path.exists():
            print(f"[-] Warning: Workflow template not found at {self.template_path}")
            # 最小限のダミー構造を返す（クラッシュ防止）
            return {}
        with open(self.template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def inject_payload(self, payload):
        """
        思想ペイロードをComfyUIのワークフローJSONの特定ノードに流し込む。
        [HERO's Mapping Logic Preserved: ノードID 6, 7, 3, 5, 10 を維持]
        """
        if not self.template:
            return {"error": "No template loaded"}

        work = json.loads(json.dumps(self.template)) # 深いコピーで原型を保護
        params = payload.get("params", {})

        # --- HERO's Node Map ---
        # 6: CLIP Text Encode (Positive) / 7: CLIP Text Encode (Negative)
        # 3: KSampler (Seed) / 5: Empty Latent Image (Resolution)
        node_map = {
            "positive": "6",
            "negative": "7",
            "seed": "3",
            "width": "5",
            "height": "5"
        }

        # プロンプトの注入
        if node_map["positive"] in work:
            work[node_map["positive"]]["inputs"]["text"] = params.get("positive_prompt", "")
        
        if node_map["negative"] in work:
            work[node_map["negative"]]["inputs"]["text"] = params.get("negative_prompt", "")

        # シード値の注入
        if node_map["seed"] in work:
            work[node_map["seed"]]["inputs"]["seed"] = params.get("seed", 0)

        # 解像度の注入
        if node_map["width"] in work:
            work[node_map["width"]]["inputs"]["width"] = params.get("resolution", {}).get("width", 832)
            work[node_map["height"]]["inputs"]["height"] = params.get("resolution", {}).get("height", 1216)

        # --- LoRAの動的注入 (HERO's Advanced Logic) ---
        # 既存のLoRAノード(ID:10)を上書き
        loras = params.get("loras", [])
        if "10" in work and loras:
            # 拡張子 .safetensors の重複付与を防止するセーフティ
            lora_name = loras[0]["name"]
            if not lora_name.endswith(".safetensors"):
                lora_name += ".safetensors"
                
            work["10"]["inputs"]["lora_name"] = lora_name
            work["10"]["inputs"]["strength_model"] = loras[0]["weight"]

        return work

if __name__ == "__main__":
    # テスト：ダミーペイロードで構造確認
    print(f"[*] Project Root: {BASE_DIR}")
    mapper = WorkflowMapper()
    
    dummy_payload = {
        "params": {
            "positive_prompt": "test positive",
            "negative_prompt": "test negative",
            "seed": 12345,
            "resolution": {"width": 832, "height": 1216},
            "loras": [{"name": "test_lora", "weight": 0.7}]
        }
    }
    
    result = mapper.inject_payload(dummy_payload)
    print("\n✅ Mapping Test Completed. (Check node 6, 7, 3, 5, 10 in output if template exists)")
