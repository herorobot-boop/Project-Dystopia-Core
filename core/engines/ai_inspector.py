import os
import json
import requests
from PIL import Image

class AIInspector:
    def __init__(self, config_path="config/h_k9_config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.threshold = 0.85

    def inspect_generation(self, image_path, original_thought, dictionary_entry):
        """
        生成画像が思想に合致しているかAI判定を行う
        """
        print(f"🔍 [AI INSPECTOR] Checking results against: {dictionary_entry}")
        
        # 判定基準の構築
        criteria = f"""
        Analyze this image based on the following thought: "{original_thought}"
        Specifically check for:
        1. Presence of '{dictionary_entry}' elements.
        2. Physical interaction (e.g., squish, penetration, fluid gloss).
        3. Camera angle (e.g., CCTV, POV, macro).
        Return a confidence score (0.0 to 1.0) and brief feedback.
        """

        # 本来はここでGPT-4o / Llava / InternVL等に画像を送信
        # ここではシミュレーション値を返すが、FAIL時は再生成フラグを立てる
        analysis_result = self._call_vlm_api(image_path, criteria)

        if analysis_result["score"] >= self.threshold:
            print(f"✅ [PASS] Score: {analysis_result['score']}. Logic satisfied.")
            return True, analysis_result["feedback"]
        else:
            print(f"❌ [FAIL] Score: {analysis_result['score']}. Reasoning: {analysis_result['feedback']}")
            return False, analysis_result["feedback"]

    def _call_vlm_api(self, image_path, prompt):
        # 実際の実装ではここでAPIリクエストを送る
        # 4090環境ならローカルのLlava等を叩く設定も可能
        return {"score": 0.9, "feedback": "Highly detailed skin tension and fluid reflection detected."}

if __name__ == "__main__":
    inspector = AIInspector()
    # テスト実行
    # inspector.inspect_generation("outputs/images/test.png", "Gym #10", "Gym#10")
