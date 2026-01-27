import json
import datetime
import random
import sys
import difflib
import os
from pathlib import Path

# --- 神経接続：プロジェクトルートの動的特定 ---
BASE_DIR = Path(__file__).resolve().parents[2]

# --- 依存モジュールのパス追加 ---
UTILS_DIR = BASE_DIR / "utils"
if str(UTILS_DIR) not in sys.path:
    sys.path.append(str(UTILS_DIR))

try:
    from lora_selector import select_lora
except ImportError:
    def select_lora(*args, **kwargs):
        print("[-] Warning: lora_selector could not be loaded from utils/")
        return []

# --- パス定義 ---
TEMPLATE_PATH = BASE_DIR / "config/logic/thought_template_master.json"
DICTIONARY_PATH = BASE_DIR / "config/dictionary/h_k9_dictionary.json"

class HK9Engine:
    def __init__(self):
        self.template = self.load_json(TEMPLATE_PATH)
        self.dictionary = self.load_json(DICTIONARY_PATH)

    def load_json(self, path):
        if not path.exists():
            print(f"[-] Warning: File not found at {path}")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def find_key_fuzzy(self, user_input):
        """聖典から『改』や『部活』をあいまい検索する"""
        query = user_input.translate(str.maketrans('０１２３４５６７８９＃', '0123456789#')).strip()
        all_keys = []
        # modificationsとeffect_parameters_extendedの両方を検索
        for cat in self.dictionary.values():
            if isinstance(cat, dict):
                all_keys.extend(cat.keys())
        
        if query in all_keys: return query
        matches = [k for k in all_keys if query in k]
        if matches: return matches[0]
        close_matches = difflib.get_close_matches(query, all_keys, n=1, cutoff=0.3)
        return close_matches[0] if close_matches else None

    def generate_thought(self, scene_input, context_type="paid"):
        """既存の高度なロジックを用いて思想を構築"""
        # 聖典から詳細な説明を取得
        key = self.find_key_fuzzy(scene_input)
        scene_context = self.dictionary.get("modifications", {}).get(key, scene_input)
        if isinstance(scene_context, dict):
            # 辞書がオブジェクト形式（改シリーズ等）の場合は名前を使用
            scene_context = scene_context.get("name", str(scene_context))
        
        ctx = self.template.get("context_matrix", {}).get(context_type, self.template["context_matrix"]["free"])
        genetics = self.template["realism_genetics"]
        
        identity_tag = random.choice([
            "1girl, japanese school girl, messy hair",
            "1girl, student, uniform"
        ])

        lora_settings = select_lora(str(scene_context), ctx["view"].lower(), context_type)

        base = {
            "project": self.template["project"],
            "timestamp": datetime.datetime.now().isoformat(),
            "selected_key": key,
            "scene_context": scene_context,
            "lora_settings": lora_settings,
            "realism_tags": genetics["tags"],
            "visual_config": {
                "view": ctx["view"],
                "focus_strategy": ctx["focus"]
            },
            "prompt_logic": {
                "applied_loras": [l['name'] for l in lora_settings] if lora_settings else [],
                "identity_direction": identity_tag
            }
        }
        return base

    def interactive_mode(self):
        """tmuxの右画面で動く対話インターフェース"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🐺 H-K9 THOUGHT GENERATOR: HYBRID-CORE")
        print("聖典の番号（例：吹奏楽部#2 / 改01）を入力してください")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        while True:
            cmd = input("H-K9 >> ")
            if cmd.lower() in ['exit', 'quit']: break
            
            try:
                thought = self.generate_thought(cmd)
                print(f"[*] 識別名: {thought['selected_key']}")
                print(f"[*] 内容: {thought['scene_context']}")
                # ここでComfyUI APIへ送信（後述の統合ポイント）
                print(f"✅ 思想射出完了。")
            except Exception as e:
                print(f"❌ エラー発生: {e}")

if __name__ == "__main__":
    engine = HK9Engine()
    engine.interactive_mode()
