import os
import json
import torch
import gc
import time
from pathlib import Path
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# =========================================================
# H-K9 Core: AI Inspector v1.0 (Omega-Blackwell)
# =========================================================

class AIInspector:
    def __init__(self, output_dir="/workspace/ComfyUI/output"):
        self.output_dir = Path(output_dir)
        self.model_id = "Qwen/Qwen2-VL-7B-Instruct"
        self.device = "cuda"
        self.threshold = 0.85  # 合格基準：SQUISH係数 0.85以上

    def _load_vlm(self):
        """検品用の『審美眼』を VRAM へ召喚"""
        print("👁️ [Inspector] Awakening Qwen2-VL (Aesthetic Audit Mode)...")
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def _unload_vlm(self):
        """検品終了後、VRAM を即座に浄化（交互覚醒の鉄則）"""
        print("🧹 [Inspector] Purging Visual Brain...")
        self.model = None
        self.processor = None
        del self.model
        del self.processor
        gc.collect()
        torch.cuda.empty_cache()

    def inspect(self, image_path, mission_id):
        """画像を視認し、聖典の要求を満たしているか判定"""
        if not os.path.exists(image_path):
            return False, "File not found."

        self._load_vlm()
        image = Image.open(image_path).convert("RGB")
        
        # 検品プロンプト：資源の定着率(SQUISH)と解剖学的正確性を問う
        prompt = (
            f"Audit this image for Mission {mission_id}. "
            "1. Is the 'viscous fluid' correctly rendered and fixed on the subject? (SQUISH score 0.0-1.0) "
            "2. Is the anatomical consistency intact? (Consistency score 0.0-1.0) "
            "Output strictly in JSON: {'squish_score': float, 'consistency_score': float, 'analysis': str}"
        )
        
        messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=[image], padding=True, return_tensors="pt").to(self.device)
        
        output_ids = self.model.generate(**inputs, max_new_tokens=256)
        response = self.processor.batch_decode(output_ids, skip_special_tokens=True)[0]
        
        self._unload_vlm()

        try:
            # JSON 抽出ロジック
            json_str = response.split("assistant\n")[-1].replace("'", '"')
            data = json.loads(json_str)
            
            passed = data['squish_score'] >= self.threshold and data['consistency_score'] >= 0.8
            msg = f"Audit Result: {'PASSED' if passed else 'FAILED'} (SQUISH: {data['squish_score']})"
            return passed, msg
        except Exception as e:
            return False, f"Audit Error: {e}"

if __name__ == "__main__":
    inspector = AIInspector()
    # テスト実行
    # passed, msg = inspector.inspect("/workspace/ComfyUI/output/test_001.png", "V2_TEST")
    # print(msg)
