import os
import json
import time
from thought_translator import ThoughtTranslator
from ai_inspector import AIInspector

class HK9Controller:
    def __init__(self):
        print("🐺 [H-K9] Initialize Controller...")
        self.translator = ThoughtTranslator()
        self.inspector = AIInspector()
        self.output_dir = "outputs/images"
        os.makedirs(self.output_dir, exist_ok=True)

    def execute_mission(self, command):
        """指定されたコード（例：行20）から生成・判定までをループ実行"""
        print(f"\n🚀 [MISSION START] Target: {command}")
        
        # 1. 翻訳（思想から物理命令へ）
        safe_prompt = self.translator.translate(command)
        print(f"🧠 [THOUGHT] Translated: {safe_prompt[:100]}...")

        # 2. 生成ループ（合格するまで最大3回試行）
        for attempt in range(1, 4):
            print(f"🎨 [GENERATE] Attempt {attempt}/3...")
            
            # 本来はここでComfyUI APIを叩いて画像を生成
            # ここではダミーパスを生成（実際はComfyUIからの出力パス）
            image_path = f"{self.output_dir}/mission_{command}_{int(time.time())}.png"
            self._call_comfy_api(safe_prompt, image_path)

            # 3. AI判定（検品）
            passed, feedback = self.inspector.inspect_image(image_path, command)
            
            if passed:
                print(f"✅ [SUCCESS] {feedback}")
                print(f"💾 [SAVE] Result stored at {image_path}")
                return True
            else:
                print(f"⚠️ [RETRY] {feedback}")
                # 失敗した場合はプロンプトを少し強化して再挑戦（デノイズ調整等）
                safe_prompt += ", increasing SQUISH intensity, extra gloss"
        
        print(f"❌ [MISSION FAILED] Could not satisfy protocols for {command}.")
        return False

    def _call_comfy_api(self, prompt, save_path):
        """ComfyUIのAPIへリクエストを飛ばす（内部実装）"""
        # ここにRunPodローカルの8188ポートへのリクエストを実装
        # 実際には画像を生成するまで待機するロジックが入ります
        pass

if __name__ == "__main__":
    controller = HK9Controller()
    while True:
        cmd = input("\n[H-K9 COMMAND] 入力してください (例: 行20, 改09, exit): ")
        if cmd.lower() == 'exit': break
        controller.execute_mission(cmd)
