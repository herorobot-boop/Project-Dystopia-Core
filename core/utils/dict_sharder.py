import json
import os
from pathlib import Path

class HK9_DictionaryManager:
    def __init__(self, source_file="/workspace/Project-Dystopia-Core/config/h_k9_dictionary.json", output_dir="/workspace/Project-Dystopia-Core/config/dictionary/"):
        self.source_path = Path(source_file)
        self.output_dir = Path(output_dir)
        self.categories = {
            "modifications": {},
            "programs": {},
            "disney": {},
            "training": {},
            "streaming": {},
            "others": {}
        }

    def auto_shard(self):
        if not self.source_path.exists():
            print(f"[ERROR] Source {self.source_path} not found.")
            return

        with open(self.source_path, 'r', encoding='utf-8') as f:
            master_data = json.load(f)

        for key, value in master_data.items():
            if key == "modifications" or key.startswith("改"):
                self.categories["modifications"][key] = value
            elif "夢の国" in key:
                self.categories["disney"][key] = value
            elif "番組" in key:
                self.categories["programs"][key] = value
            elif "筋トレ" in key:
                self.categories["training"][key] = value
            elif "配信" in key:
                self.categories["streaming"][key] = value
            else:
                self.categories["others"][key] = value
        self._save_shards()

    def _save_shards(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for cat_name, data in self.categories.items():
            if data:
                file_path = self.output_dir / f"hk9_{cat_name}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"[SUCCESS] Sharded: {file_path}")

if __name__ == "__main__":
    manager = HK9_DictionaryManager()
    manager.auto_shard()
