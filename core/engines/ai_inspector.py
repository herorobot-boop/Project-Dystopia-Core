import os
import time
import json
import torch
import gc
from pathlib import Path
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# =========================================================
# H-K9 Core: AI Inspector v1.0 (Omega-Blackwell)
# =========================================================

class AIInspector:
    def __init__(self, output_dir="/workspace/ComfyUI/output"):
        self.output_dir = Path(output_dir)
        self.model_id = "Qwen/Qwen2-VL-7B-Instruct" # 5090なら7Bは余裕で動く
        self.device = "cuda"
        self.model = None
        self.processor = None
        self.threshold = 0.85 # SQUISH（資源定着率）の合格基準

    def _load_vlm(self):
        """検品用の『審美眼』を VRAM へロード"""
        print("👁️ [Inspector] Awakening Qwen2-VL (Visual Audit Mode)...")
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def _unload_vlm(self):
        """検品終了後、即座に VRAM を解放（交互覚醒の鉄則）"""
        print("🧹 [Inspector] Purging Visual Brain...")
        del self.model
        del self.processor
        gc.collect()
        torch.cuda.empty_cache()

    def inspect_latest(self):
        """最新の生成ファイルを視認し、スコアリングを実行"""
        files = sorted(self.output_dir.glob("*.png"), key=os.path.getmtime)
        if not files:
            return None
        
        latest_file = files[-1]
        print(f"🧐 [Audit] Inspecting: {latest_file.name}")

        self._load_vlm()
        image = Image.open(latest_file).convert("RGB")
        
        # 検品用プロンプト：聖典の要求（資源定着、解剖学的正確性）を確認
        prompt = (
            "Analyze this image. Is the 'viscous fluid' correctly fixed on the target subject? "
            "Rate the 'Resource Squish (SQUISH)' from 0.0 to 1.0. "
            "Also check for anatomical consistency. Output only a JSON with 'squish_score' and 'consistency_score'."
        )
        
        messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=[text], images=[image], padding=True, return_tensors="pt").to(self.device)
        
        output_ids = self.model.generate(**inputs, max_new_tokens=128)
        response = self.processor.batch_decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        
        self._unload_vlm()

        try:
            # JSON部分のみ抽出
            json_str = response.split("assistant\n")[-1]
            score_data = json.loads(json_str)
            return score_data
        except:
            print(f"⚠️ [Warning] Failed to parse score. Raw response: {response}")
            return {"squish_score": 0.5, "consistency_score": 0.5}

    def run_audit_loop(self, commander, script_id):
        """合格するまで再送を繰り返す『無限執行ループ』"""
        while True:
            # Main_Omega.py の射出を待機（ここではシミュレート）
            print("⏳ [Waiting] Waiting for generation to complete...")
            time.sleep(60) # 生成時間を考慮

            score = self.inspect_latest()
            if not score: continue

            print(f"📊 [Result] SQUISH: {score['squish_score']}, Consistency: {score['consistency_score']}")

            if score['squish_score'] >= self.threshold:
                print("🏁 [Success] Quality Standard Met. Moving to Gdrive.")
                # ここで Gdrive への移動コマンドなどを実行
                break
            else:
                print(f"♻️ [Retry] Score {score['squish_score']} below threshold. Re-executing sequence...")
                commander.execute_sequence(script_id) # 再射出

if __name__ == "__main__":
    # Main_Omega の DystopiaCommander と連携
    inspector = AIInspector()
    # inspector.run_audit_loop(commander, "V2_執行ログ#151_1")
