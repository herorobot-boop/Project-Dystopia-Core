import os
import time
import requests
from pathlib import Path

class AIInspector:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        # 実際にはここに軽量な画像解析モデル（MoondreamやCLIP等）のAPIエンドポイントを繋ぎます
        self.api_url = "http://localhost:8188/h-k9/inspect" 

    def inspect_image(self, image_path, mission_key):
        """
        画像を解析し、聖典の要求事項（mission_key）を満たしているか判定する
        """
        print(f"🔍 [INSPECTOR] Analyzing: {image_path} for {mission_key}...")
        
        # 暫定ロジック：画像サイズやファイル実在確認（本番はVLM解析結果）
        if not os.path.exists(image_path):
            return False, "Image not found"

        # 擬似スコア判定（ここに画像解析AIの結果が入る）
        # 例: 指の数が異常、または質感が足りない場合は再試行
        score = 0.8  # デモ用スコア
        
        if score < self.threshold:
            return False, "Anatomy error or low fluid gloss"
        return True, "Passed"

    def auto_retry_loop(self, controller, mission_key, max_retries=3):
        """
        合格するまで最大N回描き直させる
        """
        for i in range(max_retries):
            image_path = controller.request_gen(mission_key)
            success, reason = self.inspect_image(image_path, mission_key)
            
            if success:
                print(f"✨ [INSPECTOR] 執行合格: {image_path}")
                return image_path
            else:
                print(f"⚠️ [INSPECTOR] 不合格 ({reason})。再試行 {i+1}/{max_retries}...")
                # プロンプトに「強調」を追加して再送
                mission_key += " (high quality, masterpiece, detailed_flesh:1.2)"
        
        return None
