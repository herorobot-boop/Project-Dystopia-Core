import json
import os
import requests
from datetime import datetime

# ==========================================================
# H-K9 Chronos Execution System - Final Version
# ----------------------------------------------------------
# 機能: 
# 1. 外部辞書(JSON)とシステムプロンプトの自動ロード
# 2. カテゴリ#番号指定による動的プロンプト生成
# 3. ローカルLLM(API)への詳細パラメータ送信
# 4. 執行結果の自動ログ保存（タイムスタンプ付き）
# ==========================================================

class ChronosExecutor:
    def __init__(self, dict_file='h_k9_dictionary.json', prompt_file='system_prompt.txt', log_dir='logs'):
        self.dict_file = dict_file
        self.prompt_file = prompt_file
        self.log_dir = log_dir
        self.api_url = "http://localhost:11434/api/generate"  # Ollamaの標準エンドポイント
        self.model_name = "chronos-hermes-13b" # 使用するローカルモデル名

        # ログディレクトリの自動作成
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
            return "You are a cold-hearted H-K9 executioner."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_log(self, key, response):
        """執行結果をテキストファイルとして物理保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.log_dir}/execution_{key}_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"--- H-K9 EXECUTION LOG ---\n")
            f.write(f"ID: {key}\n")
            f.write(f"DATE: {timestamp}\n")
            f.write(f"--------------------------\n\n")
            f.write(response)
        print(f"[*] 執行記録をアーカイブしました: {filename}")

    def execute(self, category, number):
        """Chronosに特定のシチュエーションを執行させる"""
        key = f"{category}#{number}"
        
        if key not in self.dictionary:
            print(f"[-] ID '{key}' は辞書に定義されていません。")
            return

        detail = self.dictionary[key]
        print(f"[*] ターゲット特定: {key}")
        print(f"[*] コンテキスト注入開始...")

        # Chronosへの命令セット
        user_input = (
            f"### 執行命令発令\n"
            f"識別ID: {key}\n"
            f"執行詳細コンテキスト: {detail}\n\n"
            f"最終指示: 辞書定義とシステムプロンプトに従い、"
            f"肉体の歪み(Squish)、資源汚染、および記録デバイスの視点を"
            f"極限まで強調した叙述を展開せよ。"
        )

        payload = {
            "model": self.model_name,
            "system": self.system_prompt,
            "prompt": user_input,
            "stream": False,
            "options": {
                "temperature": 0.8,      # 描写の多様性を確保
                "top_p": 0.9,            # 語彙の質を維持
                "num_predict": 2048,     # 長文出力を許可
                "repeat_penalty": 1.2    # 同じ描写の繰り返しを抑制
            }
        }

        try:
            # タイムアウトを長めに設定（詳細な描写を生成するため）
            response = requests.post(self.api_url, json=payload, timeout=600)
            response.raise_for_status()
            result = response.json().get('response', '')
            
            print("\n" + "="*40)
            print(f" CHRONOS OUTPUT: {key}")
            print("="*40 + "\n")
            print(result)
            print("\n" + "="*40 + "\n")
            
            self.save_log(key, result)
            
        except requests.exceptions.RequestException as e:
            print(f"[-] 執行エラー: ローカルLLMサーバーに接続できません。\n{e}")

if __name__ == "__main__":
    # システム初期化
    executor = ChronosExecutor()

    print("\n--- H-K9 Professional Execution Terminal ---")
    print("有効なカテゴリ: 医療, ジム, 服, 問, 無視, 浴, 特, 舞, 産, 行")
    
    while True:
        cmd = input("\n執行命令を入力してください (例: 行 20 / 終了時は 'exit'): ")
        if cmd.lower() == 'exit':
            break
            
        try:
            parts = cmd.split()
            if len(parts) != 2:
                print("形式エラー: 'カテゴリ 番号' の形式で入力してください。")
                continue
            
            cat, num = parts
            executor.execute(cat, num)
        except Exception as e:
            print(f"[-] 予期せぬエラー: {e}")
