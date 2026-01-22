import json
from pathlib import Path

class WorkflowMapper:
    def __init__(self, template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            self.template = json.load(f)

    def inject_payload(self, payload):
        """
        思想ペイロードをComfyUIのワークフローJSONの特定ノードに流し込む。
        ※ノードIDは、あなたの使用する標準ワークフローに合わせて調整が必要です。
        """
        work = self.template.copy()
        params = payload["params"]

        # --- マッピング設定（例：標準的なSDXL/Fluxワークフローを想定） ---
        # 6: CLIP Text Encode (Positive)
        # 7: CLIP Text Encode (Negative)
        # 3: KSampler (Seed)
        # 5: Empty Latent Image (Resolution)
        
        # ※実際のワークフローJSONを開いて、IDを書き換える必要があります。
        node_map = {
            "positive": "6",
            "negative": "7",
            "seed": "3",
            "width": "5",
            "height": "5"
        }

        # プロンプトの注入
        if node_map["positive"] in work:
            work[node_map["positive"]]["inputs"]["text"] = params["positive_prompt"]
        
        if node_map["negative"] in work:
            work[node_map["negative"]]["inputs"]["text"] = params["negative_prompt"]

        # シード値の注入
        if node_map["seed"] in work:
            work[node_map["seed"]]["inputs"]["seed"] = params["seed"]

        # 解像度の注入
        if node_map["width"] in work:
            work[node_map["width"]]["inputs"]["width"] = params["resolution"]["width"]
            work[node_map["height"]]["inputs"]["height"] = params["resolution"]["height"]

        # --- LoRAの動的注入 (Advanced) ---
        # LoRAはノードを「増やす」必要があるため、
        # ここではシンプルに「既存のLoRAノード(ID:10)」を上書きする例
        if "10" in work and params["loras"]:
            work["10"]["inputs"]["lora_name"] = params["loras"][0]["name"] + ".safetensors"
            work["10"]["inputs"]["strength_model"] = params["loras"][0]["weight"]

        return work

if __name__ == "__main__":
    # テスト：ダミーのテンプレートとペイロードでマッピング
    print("Workflow Mapping Logic Initialized.")
