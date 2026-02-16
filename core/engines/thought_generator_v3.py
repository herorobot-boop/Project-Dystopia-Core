import json
import difflib
import sys
from pathlib import Path

# --- インポート先を core/engines に固定 ---
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

try:
    from thought_translator import ThoughtTranslatorV2
except ImportError:
    print("[-] Error: thought_translator.py not found in the same directory.")
    sys.exit(1)

# =========================================================
# H-K9 Core: Thought Generator V3 (Plan-A Controller)
# =========================================================

class HK9EngineV2:
    def __init__(self):
        self.translator = ThoughtTranslatorV2()
        # 辞書の全キー（v2_id, original_idなど）をインデックス化
        self.all_keys = list(self.translator.dictionary.keys())

    def find_key_fuzzy(self, user_input):
        """聖典からキーをあいまい検索（全角半角・部分一致対応） [7]"""
        # 全角英数を半角にし、空白を除去して正規化
        query = user_input.translate(str.maketrans('０１２３４５６７８９＃', '0123456789#')).strip()
        
        if query in self.all_keys:
            return query
            
        # 部分一致検索
        matches = [k for k in self.all_keys if query in k]
        if matches:
            return matches
            
        # 類似度検索
        close_matches = difflib.get_close_matches(query, self.all_keys, n=1, cutoff=0.3)
        return close_matches if close_matches else None

    def execute_thought(self, user_input):
        """思想展開の執行"""
        selected_key = self.find_key_fuzzy(user_input)
        
        if not selected_key:
            print(f"[-] ターゲット未特定: {user_input}")
            return None

        print(f"🎯 [TARGET_LOCKED]: {selected_key}")
        
        # 強度判定ロジック
        intensity = 0.95 if any(x in user_input for x in ["極限", "高強度", "激しく"]) else 0.8
        
        # V2翻訳執行
        payload = self.translator.translate_v2(selected_key, intensity=intensity)
        return payload

    def interactive_mode(self):
        """tmuxの右画面で動作する対話ターミナル [9]"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🐺 H-K9 THOUGHT GENERATOR: V2-INTEGRATED")
        print("聖典ID（例：SIT_PROG_010_A1）または『番組#10』等を入力")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        while True:
            cmd = input("H-K9 >> ")
            if cmd.lower() in ['exit', 'quit']: break
            if not cmd: continue
            
            result = self.execute_thought(cmd)
            if result:
                print(f"[*] 射出準備完了: {result['positive'][:80]}...")
                print(f"[*] Denoise: {result['denoise']} / CFG: {result['cfg']}")

if __name__ == "__main__":
    engine = HK9EngineV2()
    if len(sys.argv) > 1 and sys.argv[10] == "--interactive":
        engine.interactive_mode()
    else:
        # デフォルトはテスト実行
        test_cmd = "CM明け"
        engine.execute_thought(test_cmd)
