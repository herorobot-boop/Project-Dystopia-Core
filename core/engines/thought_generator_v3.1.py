# =========================================================
# H-K9 Core: Thought Generator v3.1 (Full Sacred-Dict Integration)
# =========================================================
import json
import os
from pathlib import Path

class ThoughtEngine:
    def __init__(self):
        # 4000行の聖典パス
        self.dict_path = Path("/workspace/Project-Dystopia-Core/config/h_k9_dictionary.json")
        self.load_master_dictionary()

    def load_master_dictionary(self):
        """巨大な聖典をメモリにロードし、インデックス化する"""
        if not self.dict_path.exists():
            print(f"❌ [H-K9] ERROR: Dictionary not found at {self.dict_path}")
            self.data = {}
            return
        
        with open(self.dict_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # 統計ログ
        mod_count = len(self.data.get("modifications", {}))
        prog_count = len([k for k in self.data.keys() if "番組" in k or "夢の国" in k])
        print(f"📚 [H-K9] Holy Dictionary Loaded.")
        print(f"   - Modifications: {mod_count} types")
        print(f"   - Simulation Scenarios: Over {prog_count} entries")

    def extract_scenario(self, user_input):
        """辞書の全キーをスキャンし、マッチするシナリオ内容を抽出する"""
        scenario_text = ""
        # modification以外の全てのキー（番組#、夢の国#など）を検索対象にする
        for key, value in self.data.items():
            if key in ["modifications", "archive_metadata"]:
                continue
            if key in user_input:
                scenario_text += f" [SCENARIO_LOG: {value}]"
        return scenario_text

    def translate_thought(self, user_input, target_model="Z-Image"):
        """
        聖典の「狂気」を Z-Image 用の「物理演算プロンプト」へコンパイルする
        """
        # デフォルト設定（Z-Image/5090 最適化値）
        payload = {
            "positive": "",
            "negative": "smooth skin, plastic, AI-perfection, airbrushed, cinematic filter, doll-like, makeup",
            "cfg": 4.2,
            "denoise": 0.42,
            "steps": 40
        }

        # 1. 物理改変（改シリーズ）の適用
        mods = self.data.get("modifications", {})
        applied_mods = []
        for code, details in mods.items():
            if code in user_input:
                payload["positive"] += f"({details['effect']}:1.2), ({details['physics']}:1.3), "
                payload["denoise"] = details.get("denoise", payload["denoise"])
                applied_mods.append(details['name'])

        # 2. 聖典シナリオの抽出（番組# / 夢の国# 等）
        scenario_content = self.extract_scenario(user_input)
        
        # 3. Z-Image「引き算の美学」との融合
        # 事務的な報告調を維持しつつ、物理的な詳細（毛穴、peach fuzz等）を強制
        base_quality = "score_9, photorealistic, raw handheld photo, visible pores, fine peach fuzz, subsurface scattering, digital noise"
        
        final_prompt = (
            f"{base_quality}, {payload['positive']} "
            f"Subject: {user_input}, Context: {scenario_content}, "
            f"Style: Administrative report style, no emotional expression."
        )

        payload["positive"] = final_prompt
        payload["applied_modifications"] = applied_mods
        return payload

    def run_interactive(self):
        print("\n🐺 [H-K9] Thought Engine v3.1: Execution Terminal")
        print("👉 実行例: '改09 夢の国執行#28 手すりに寄りかかるマン筋'")
        while True:
            ui = input("\n👉 Command Input: ")
            if ui.lower() == 'exit': break
            
            res = self.translate_thought(ui)
            print("\n✨ [FINAL PAYLOAD FOR COMPILING]")
            print(json.dumps(res, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    engine = ThoughtEngine()
    engine.run_interactive()
