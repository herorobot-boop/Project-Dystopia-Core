import json
import requests
from datetime import datetime
from pathlib import Path

# ==========================================================
# H-K9 Chronos Execution System - Standardized Version
# ----------------------------------------------------------
# [システム統一：vLLM/OpenAI API 規格適合]
# ==========================================================

class ChronosExecutor:
    def __init__(self):
        # プロジェクトのルートディレクトリを自動特定
        self.base_dir = Path(__file__).resolve().parents[2]
        
        # 整理された新構造に基づくパス設定
        self.dict_file = self.base_dir / 'config/dictionary/h_k9_dictionary.json'
        self.prompt_file = self.base_dir / 'core/protocols/system_prompt.txt'
        self.log_dir = self.base_dir / 'outputs/payload_logs'
        
        # システム全体の通信規格を統一 (vLLM / v1 / completions)
        self.api_url = "http://localhost:11434/v1/chat/completions"
        self.model_name = "chronos-hermes-13b"

        # ログディレクトリの自動作成
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # データの読み込み
        self.dictionary = self._load_json(self.dict_file)
        self.system_prompt = self._load_text(self.prompt_file)

    def _load_json(self, path):
        if not path.exists():
            print(f"Error: {path} が見つかりません。")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_text(self, path):
        if not path.exists():
            print(f"Error: {path} が見つかりません。")
            return "You are a cold-hearted H-K9 executioner."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_log(self, key, response):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir / f"execution_{key}_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"--- H-K9 EXECUTION LOG ---\nID: {key}\nDATE: {timestamp}\n{'-'*26}\n\n{response}")
        print(f"[*] 執行記録をアーカイブしました: {filename}")

    def execute(self, category, number):
        key = f"{category}#{number}"
        if key not in self.dictionary:
            print(f"[-] ID '{key}' は辞書に定義されていません。")
            return

        detail = self.dictionary[key]
        print(f"[*] ターゲット特定: {key}")
        
        # vLLM / OpenAI互換形式のメッセージ構造
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"### 執行命令発令\n識別ID: {key}\n執行詳細コンテキスト: {detail}\n\n最終指示: 辞書定義とシステムプロンプトに従い、肉体の歪み(Squish)、資源汚染、記録デバイスの視点を極限まで強調した叙述を展開せよ。"}
            ],
            "temperature": 0.8,
            "max_tokens": 2048
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=600)
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content']
            print(f"\n{'='*40}\n CHRONOS OUTPUT: {key}\n{'='*40}\n\n{result}\n\n{'='*40}\n")
            self.save_log(key, result)
        except Exception as e:
            print(f"[-] 執行エラー: {e}")

if __name__ == "__main__":
    executor = ChronosExecutor()
    print("\n--- H-K9 Professional Execution Terminal (Unified API Mode) ---")
    while True:
        cmd = input("\n執行命令 (例: 浴 9 / exit): ")
        if cmd.lower() == 'exit': break
        try:
            parts = cmd.split()
            if len(parts) == 2: executor.execute(parts[0], parts[1])
            else: print("形式エラー: 'カテゴリ 番号' で入力してください。")
        except Exception as e: print(f"[-] エラー: {e}")
