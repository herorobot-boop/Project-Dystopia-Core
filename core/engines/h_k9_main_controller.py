import json
import urllib.request
import urllib.parse
import uuid
import time
import os
import sys

# 自作エンジンのインポート（パスが通っている前提）
try:
    from thought_translator import ThoughtTranslator
    from ai_inspector import AIInspector
except ImportError:
    print("⚠️ [警告] 依存エンジンが見つかりません。スタブモードで動作します。")

class HK9Controller:
    def __init__(self, server_address="127.0.0.1:8188"):
        print("🐺 [H-K9] 統合司令エンジン (Headless Expansion Edition) 起動...")
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.target_node_id = None
        self.output_dir = "outputs/images"
        self.workflow_path = "config/workflows/h_k9_standard_workflow.json"
        
        # 翻訳・判定エンジンの初期化
        self.translator = ThoughtTranslator()
        self.inspector = AIInspector()
        
        os.makedirs(self.output_dir, exist_ok=True)

    def _find_prompt_node(self, workflow):
        """画面を見ずにJSONからプロンプトノードを自動特定する心臓部"""
        if self.target_node_id and self.target_node_id in workflow:
            return self.target_node_id

        candidates = []
        for node_id, node_info in workflow.items():
            if node_info.get("class_type") == "CLIPTextEncode":
                current_text = node_info.get("inputs", {}).get("text", "")
                candidates.append({"id": node_id, "text": current_text})

        if not candidates:
            print("❌ [ERROR] ワークフロー内に CLIPTextEncode ノードが見つかりません。")
            sys.exit(1)

        # 候補が1つなら即断
        if len(candidates) == 1:
            self.target_node_id = candidates[0]["id"]
            return self.target_node_id

        # 複数ある場合、ネガティブワードが含まれていない方をポジティブと推論
        negative_hints = ["low quality", "bad anatomy", "text", "watermark", "error"]
        for c in candidates:
            if not any(word in c["text"].lower() for word in negative_hints):
                self.target_node_id = c["id"]
                print(f"🎯 [AUTO-DETECT] Node ID '{c['id']}' をポジティブ用と推論しました。")
                return self.target_node_id

        # 推論に失敗した場合のみ対話形式で確認
        print("\n⚠️  [ALERT] 複数の入力ノードを検出。どちらに書き込みますか？")
        for i, c in enumerate(candidates):
            print(f"  [{i}] ID: {c['id']} (現在の内容: {c['text'][:40]}...)")
        
        choice = input("👉 番号を選択 (0 または 1): ")
        self.target_node_id = candidates[int(choice)]["id"]
        return self.target_node_id

    def _queue_prompt(self, workflow_json):
        p = {"prompt": workflow_json, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read())

    def _wait_and_receive(self, prompt_id):
        """生成完了を待機して画像を保存"""
        print("⏳ [GENERATE] ComfyUI描画中...", end="", flush=True)
        while True:
            with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as res:
                history = json.loads(res.read())
                if prompt_id in history:
                    print("完了！")
                    return history[prompt_id]['outputs']
            print(".", end="", flush=True)
            time.sleep(1)

    def _save_image(self, filename, subfolder, folder_type, mission_id):
        params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": folder_type})
        with urllib.request.urlopen(f"http://{self.server_address}/view?{params}") as res:
            img_data = res.read()
            path = f"{self.output_dir}/{mission_id}_{int(time.time())}.png"
            with open(path, "wb") as f:
                f.write(img_data)
            return path

    def execute_mission(self, command):
        """思想を現実（画像）へ変換する全工程"""
        print(f"\n🚀 [MISSION] ターゲット執行: {command}")
        
        # 1. 思想翻訳
        safe_prompt = self.translator.translate(command)
        
        # 2. ワークフロー読み込み
        if not os.path.exists(self.workflow_path):
            print(f"❌ [ERROR] {self.workflow_path} がありません。")
            return

        with open(self.workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)

        # 3. ノード特定とプロンプト注入
        node_id = self._find_prompt_node(workflow)
        workflow[node_id]["inputs"]["text"] = safe_prompt

        # 4. 生成・判定ループ
        for attempt in range(1, 4):
            print(f"🌀 [ATTEMPT {attempt}/3]")
            res = self._queue_prompt(workflow)
            prompt_id = res['prompt_id']
            
            outputs = self._wait_and_receive(prompt_id)
            
            last_image = None
            for node in outputs:
                if 'images' in outputs[node]:
                    for img in outputs[node]['images']:
                        last_image = self._save_image(img['filename'], img['subfolder'], img['type'], command)

            # 5. AI検品
            if last_image:
                passed, feedback = self.inspector.inspect(last_image, command)
                if passed:
                    print(f"✅ [CLEARED] 資源定着成功: {last_image}")
                    return
                else:
                    print(f"⚠️ [REJECTED] 判定不合格: {feedback}")
                    # 再試行用にプロンプトを自動強化
                    workflow[node_id]["inputs"]["text"] += ", intense resource overflow, ultra-high skin gloss"
        
        print(f"❌ [FAILED] {command} の自動執行プロトコルは完遂できませんでした。")

if __name__ == "__main__":
    controller = HK9Controller()
    while True:
        cmd = input("\n[H-K9] 執行コード入力 (例: 行20, 検#10, exit): ")
        if cmd.lower() == 'exit': break
        controller.execute_mission(cmd)
