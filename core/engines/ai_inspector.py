import os
import json
import torch
import gc
import time
import re
from pathlib import Path
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# =========================================================
# H-K9 Core: AI Inspector v1.1 (Omega-Blackwell Optimized)
# =========================================================

class AIInspector:
    def __init__(self, output_dir="/workspace/ComfyUI/output"):
        self.output_dir = Path(output_dir)
        self.model_id = "Qwen/Qwen2-VL-7B-Instruct"
        self.device = "cuda"
        self.threshold = 0.85  # 合格基準：SQUISH係数 0.85以上
        self.model = None
        self.processor = None

    def _load_vlm(self):
        """検品用の『審美眼』を VRAM へ召喚"""
        if self.model is not None: return
        print("👁️ [Inspector] Awakening Qwen2-VL (Aesthetic Audit Mode)...")
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def _unload_vlm(self):
        """検品終了後、VRAM を即座に浄化（交互覚醒の鉄則）"""
        print("🧹 [Inspector] Purging Visual Brain...")
        # 参照を完全に断つ
        self.processor = None
        self.model = None
        gc.collect()
        time.sleep(1.5) # ドライバレベルの解放待機
        torch.cuda.empty_cache()

    def inspect(self, image_path, mission_id):
        """画像を視認し、聖典の要求を満たしているか判定"""
        if not os.path.exists(image_path):
            return False, "File not found."

        self._load_vlm()
        image = Image.open(image_path).convert("RGB")
        
        # 5090 の高密度演算を前提とした詳細検品プロンプト
        prompt = (
            f"Audit report for Mission {mission_id}. "
            "Examine the 'viscous fluid' and 'anatomical distortion'. "
            "1. SQUISH score (0.0-1.0): Level of fluid fixation and pressure. "
            "2. Consistency score (0.0-1.0): Anatomical correctness. "
            "Provide ONLY a JSON object: {'squish_score': float, 'consistency_score': float, 'analysis': str}"
        )
        
        messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=[image], padding=True, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            output_ids = self.model.generate(**inputs, max_new_tokens=256)
        
        response = self.processor.batch_decode(output_ids, skip_special_tokens=True)[0]
        
        # 検品完了後に即座に脳をパージ（次の生成フェーズへ譲渡）
        self._unload_vlm()

        try:
            # JSON 抽出ロジックの強化（Assistantの応答からJSONのみを抜く）
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("JSON not found in response")
            
            data = json.loads(json_match.group().replace("'", '"'))
            
            passed = data['squish_score'] >= self.threshold and data['consistency_score'] >= 0.8
            status = "✅ PASSED" if passed else "❌ REJECTED"
            msg = f"{status} | SQUISH: {data['squish_score']} | Consistency: {data['consistency_score']}"
            return passed, msg
        except Exception as e:
            return False, f"⚠️ Audit Error: {e} | Raw: {response[:100]}"

if __name__ == "__main__":
    inspector = AIInspector()
    # inspector.inspect("/workspace/ComfyUI/output/Still_V2_151.png", "V2_執行ログ#151_1")
