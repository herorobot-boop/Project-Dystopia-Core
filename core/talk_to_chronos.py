import json
import os
import requests
from datetime import datetime

# ==========================================================
# H-K9 Chronos Execution System
# ----------------------------------------------------------
# このスクリプトは、指定されたカテゴリと番号から
# 辞書データを読み込み、システムプロンプトと共に
# ローカルLLM(Chronos)へ送信し、出力を記録します。
# ==========================================================

class ChronosExecutor:
    def __init__(self, dict_file='h_k9_dictionary.json', prompt_file='system_prompt.txt', log_dir='logs'):
        self.dict_file = dict_file
        self.prompt_file = prompt_file
        self.log_dir = log_dir
        self.api_url = "http://localhost:11434/api/generate"  # Ollamaなどの標準APIポート
        self.model_name = "chronos-hermes-13b" # 使用するモデル名

        # ログディレクトリの作成
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # データの読み込み
        self.dictionary = self._load_json(self.dict_file)
        self.system_prompt = self._load_text(self.prompt_file)

    def _load_json(self, path):
        if not os.path.exists(path):
            print(f"Error: {path} が見つかりません。")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_text(self, path):
        if not os.path.exists(path):
            print(f"Error: {path} が見つかりません。")
            return "You are an AI assistant."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_log(self, key, response):
        """執行結果をテキストファイルとして保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.log_dir}/execution_{key}_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"--- EXECUTION LOG ---\n")
            f.write(f"ID: {key}\n")
            f.write(f"DATE: {timestamp}\n")
            f.write(f"---------------------\n\n")
            f.write(response)
        print(f"[*] 記録を保存しました: {filename}")

    def execute(self, category, number):
        """指定された番号のシチュエーションをChronosに執行させる"""
        key = f"{category}#{number}"
        
        if key not in self.dictionary:
            print(f"[-] {key} は辞書に存在しません。")
            return

        detail = self.dictionary[key]
        print(f"[*] 執行準備完了: {key}")
        print(f"[*] 詳細コンテキストを注入中...")

        # Chronosへの最終入力構成
        user_input = (
            f"### 執行命令発令\n"
            f"識別ID: {key}\n"
            f"執行コンテキスト: {detail}\n\n"
            f"指示: 上記コンテキストを、辞書定義に基づいた物理描写、"
            f"資源汚染、記録の背徳感を伴う詳細な叙述で展開せよ。"
        )

        payload = {
            "model": self.model_name,
            "system": self.system_prompt,
            "prompt": user_input,
            "stream": False,
            "options": {
                "temperature": 0.8, # 描写の広がりを持たせる
                "top_p": 0.9,
                "num_predict": 2048 # 出力長を十分に確保
            }
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json().get('response', '')
            
            print("\n=== CHRONOS OUTPUT ===\n")
            print(result)
            print("\n======================\n")
            
            self.save_log(key, result)
            
        except requests.exceptions.RequestException as e:
            print(f"[-] APIエラーが発生しました: {e}")

if __name__ == "__main__":
    # 初期化
    executor = ChronosExecutor()

    # CUIインターフェース
    print("--- H-K9 Execution Terminal ---")
    print("例: 医療 1, ジム 25, 行 10")
    
    cmd = input("執行するカテゴリと番号を入力してください (例: 医療 1): ")
    try:
        cat, num = cmd.split()
        executor.execute(cat, num)
    except ValueError:
        print("入力形式が正しくありません。'カテゴリ 番号'の形式で入力してください。")
