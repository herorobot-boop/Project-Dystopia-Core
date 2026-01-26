import json
import urllib.request
import urllib.parse
import uuid
import time
import os
from thought_translator import ThoughtTranslator
from ai_inspector import AIInspector

class HK9Controller:
    def __init__(self, server_address="127.0.0.1:8188"):
        print("🐺 [H-K9] 統合司令エンジン 起動...")
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.translator = ThoughtTranslator()
        self.inspector = AIInspector()
        self.output_dir = "outputs/images"
        os.makedirs(self.output_dir, exist_ok=True)

    def _queue_prompt(self, prompt_workflow):
        """ComfyUIにワークフローを送信"""
        p = {"prompt": prompt_workflow, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())

    def _get_history(self, prompt_id):
        """生成完了を確認し、履歴を取得"""
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def _get_image(self, filename, subfolder, folder_type):
        """生成された画像バイナリを取得し保存"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

    def execute_mission(self, command):
        """思想翻訳 -> ComfyUI生成 -> AI検品 の自動ループ"""
        print(f"\n🚀 [MISSION START] ターゲット: {command}")
        
        # 1. 翻訳プロトコル
        safe_prompt = self.translator.translate(command)
        print(f"🧠 [THOUGHT] 翻訳完了: {safe_prompt[:50]}...")

        # 2. ワークフローの準備 (workflow_api.json を読み込む)
        # ※ComfyUIから 'Save API Format' で書き出したJSONが必要です
        try:
            with open("config/workflows/h_k9_standard_workflow.json", "r", encoding="utf-8") as f:
                workflow = json.load(f)
        except FileNotFoundError:
            print("❌ エラー: config/workflows/h_k9_standard_workflow.json が見つかりません。")
            return

        # プロンプトの注入 (Node ID '6' が CLIP Text Encode と想定)
        # あなたの環境に合わせて ID '6' や 'inputs' の場所を調整してください
        workflow["6"]["inputs"]["text"] = safe_prompt

        # 3. 生成・検品ループ
        for attempt in range(1, 4):
            print(f"🎨 [GENERATE] 試行 {attempt}/3...")
            enqueue_res = self._queue_prompt(workflow)
            prompt_id = enqueue_res['prompt_id']

            # 生成完了待機
            while True:
                history = self._get_history(prompt_id)
                if prompt_id in history:
                    break
                time.sleep(1) # 1秒待機

            # 画像の抽出と保存
            outputs = history[prompt_id]['outputs']
            for node_id in outputs:
                for image_data in outputs[node_id].get('images', []):
                    image_bytes = self._get_image(image_data['filename'], image_data['subfolder'], image_data['type'])
                    file_path = f"{self.output_dir}/{command}_att{attempt}.png"
                    with open(file_path, "wb") as f:
                        f.write(image_bytes)

            # 4. AI判定
            passed, feedback = self.inspector.inspect(file_path, command)
            if passed:
                print(f"✅ [SUCCESS] プロトコル合致: {feedback}")
                return file_path
            else:
                print(f"⚠️ [RETRY] 判定不合格: {feedback}")
                # プロンプトに物理定着の命令を強調
                workflow["6"]["inputs"]["text"] += ", high-viscosity surface coating, intense body indentation"

        print(f"❌ [FAILED] {command} の資源定着に失敗しました。")
        return None

if __name__ == "__main__":
    controller = HK9Controller()
    while True:
        target = input("\n[H-K9] 執行コードを入力 (例: 行20, 検#15, exit): ")
        if target.lower() == 'exit': break
        controller.execute_mission(target)
