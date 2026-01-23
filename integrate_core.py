import os
import shutil
from pathlib import Path

# --- 最終確定構成：Project-Dystopia-Core ---
PROJECT_NAME = "Project-Dystopia-Core"
BASE_DIR = Path(f"/workspace/{PROJECT_NAME}")

# 内部ディレクトリ構造
CORE_DIR = BASE_DIR / "core"
CONFIG_DIR = BASE_DIR / "config"
OUTPUTS_DIR = BASE_DIR / "outputs"

# 作成すべき全フォルダリスト
SUB_DIRS = [
    CORE_DIR,
    CONFIG_DIR,
    OUTPUTS_DIR / "payload_logs",
    OUTPUTS_DIR / "images",
    OUTPUTS_DIR / "evolved_thoughts",
]

# core（知性の柱）へ移動
CORE_FILES = [
    "thought_generator.py", "lora_selector.py", "prompt_builder.py",
    "prompt_to_comfy.py", "workflow_mapper.py", "comfy_client.py",
    "run_batch.py", "run_evolved_batch.py", "result_watcher.py",
    "evaluator.py", "score_thoughts.py", "evolution_tracker.py",
    "mutation_lab.py", "bloodline_viewer.py"
]

# config（設定・器）へ移動
CONFIG_FILES = [
    "workflow_api_template.json", "lora_assets.csv", "mutation_patterns.json"
]

def run_integration():
    print(f"🏗️ --- Project-Dystopia-Core: 最終統合を開始します ---")

    # 1. ルートディレクトリとサブディレクトリの作成
    for d in SUB_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {d.relative_to(Path('/workspace'))}")

    # 2. ファイルの移動（/workspace または /workspace/Project-Dystopia から）
    # 以前のディレクトリ名がある場合も考慮
    old_base = Path("/workspace/Project-Dystopia")
    
    def smart_move(file_list, target_dir):
        for f_name in file_list:
            # 検索候補：現在のカレント、旧ディレクトリ
            candidates = [Path("/workspace") / f_name, old_base / f_name]
            moved = False
            for src in candidates:
                if src.exists():
                    dst = target_dir / f_name
                    shutil.move(str(src), str(dst))
                    print(f"🚀 Moved: {f_name} -> {target_dir.name}/")
                    moved = True
                    break
            
            if not moved and not (target_dir / f_name).exists():
                # 空のファイルを作成しておく（器の準備）
                (target_dir / f_name).touch()
                print(f"📝 Initialized (Empty): {f_name} -> {target_dir.name}/")

    smart_move(CORE_FILES, CORE_DIR)
    smart_move(CONFIG_FILES, CONFIG_DIR)

    # 3. .gitignore の作成
    gitignore_content = """# Python
__pycache__/
*.pyc

# Project Outputs (Non-sync)
outputs/images/*
outputs/payload_logs/*
outputs/evolved_thoughts/*
outputs/thought_log.jsonl

# Config Secrets
config/workflow_api_template.json
"""
    with open(BASE_DIR / ".gitignore", "w") as f:
        f.write(gitignore_content)
    print("📝 Created: .gitignore")

    print(f"\n✅ 全工程完了。")
    print(f"📂 場所: {BASE_DIR}")
    print(f"💡 次は 'cd {PROJECT_NAME}' で中身を確認してください。")

if __name__ == "__main__":
    run_integration()
