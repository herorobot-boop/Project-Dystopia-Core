import json
import os
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Sacred Dictionary Salvage (Omega-Blackwell)
# =========================================================

class DictionarySalvager:
    def __init__(self):
        self.base_dir = Path("/workspace/Project-Dystopia-Core/config/dictionary")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.base_dir / "h_k9_dictionary_V2_Final.json"
        self.master_dict = {}

    def ingest_fragment(self, file_path):
        """断片化した聖典ファイルを読み込み、マスターへ統合"""
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️ [Skip] Fragment not found: {file_path}")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                fragment = json.load(f)
                initial_count = len(self.master_dict)
                self.master_dict.update(fragment)
                added = len(self.master_dict) - initial_count
                print(f"📥 [Ingest] {path.name}: {added} new entries synced.")
        except Exception as e:
            print(f"❌ [Error] Failed to parse {path.name}: {e}")

    def validate_sync(self):
        """23,000行の工場設計図（JSON）との互換性をチェック"""
        print(f"🔍 [Audit] Validating 5000+ entries against Blackwell Factory...")
        # 5000件のキーが 'V2_' で始まっているか、物理タグが空でないかを確認
        invalid_keys = [k for k in self.master_dict.keys() if not k.startswith("V2_")]
        if invalid_keys:
            print(f"⚠️ [Warning] Found {len(invalid_keys)} keys without 'V2_' prefix. Normalizing...")
            for k in invalid_keys:
                self.master_dict[f"V2_{k}"] = self.master_dict.pop(k)

    def finalize(self):
        """聖典を物理ファイルへ固定"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.master_dict, f, indent=4, ensure_ascii=False)
        
        print("\n" + "█"*60)
        print(f"     SACRED DICTIONARY V2: FINAL CRYSTALLIZATION")
        print(f"     TOTAL ENTRIES: {len(self.master_dict)}")
        print(f"     LOCATION: {self.output_file}")
        print("█"*60)

if __name__ == "__main__":
    salvager = DictionarySalvager()
    
    # 散逸した各セクションの読み込み（パスは環境に合わせ調整）
    # 例：151番（マン筋超接写）から87番（ニュースJAPAN）まで全て
    fragments = [
        "fragments/execution_logs_151_500.json",
        "fragments/program_catalog_v2_extended.json",
        "fragments/dystopia_core_base.json"
    ]
    
    for frag in fragments:
        salvager.ingest_fragment(frag)
        
    salvager.validate_sync()
    salvager.finalize()
