import os
import shutil
from pathlib import Path

PROJECT_NAME = "Project-Dystopia-Core"
BASE_DIR = Path(f"/workspace/{PROJECT_NAME}")

# サブフォルダ定義
CORE_DIR = BASE_DIR / "core"
CONFIG_DIR = BASE_DIR / "config"
OUTPUTS_DIR = BASE_DIR / "outputs"
LEGACY_DIR = BASE_DIR / "legacy"
WF_DIR = BASE_DIR / "workflows"

def organize_final():
    # 1. 構造作成
    for d in [CORE_DIR, CONFIG_DIR, OUTPUTS_DIR, LEGACY_DIR, WF_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    for sub in ["payload_logs", "images", "evolved_thoughts"]:
        (OUTPUTS_DIR / sub).mkdir(parents=True, exist_ok=True)

    # 2. 移動ルール設定
    # { "現在のファイル名": "移動後の名前" }
    mapping = {
        # 知性の中枢 (Core)
        "thought_generator.py": CORE_DIR / "thought_generator.py",
        "lora_selector.py": CORE_DIR / "lora_selector.py",
        "prompt_builder.py": CORE_DIR / "prompt_builder.py",
        "prompt_to_comfy.py": CORE_DIR / "prompt_to_comfy.py",
        "run_batch.py": CORE_DIR / "run_batch.py",
        "run_evolved_batch.py": CORE_DIR / "run_evolved_batch.py",
        "result_watcher.py": CORE_DIR / "result_watcher.py",
        "evaluator.py": CORE_DIR / "evaluator.py",
        "score_thoughts.py": CORE_DIR / "score_thoughts.py",
        "evolution_tracker.py": CORE_DIR / "evolution_tracker.py",
        "bloodline_viewer.py": CORE_DIR / "bloodline_viewer.py",
        "chronos_mapper_v3_2.py": CORE_DIR / "workflow_mapper.py", # 改名統合
        
        # 設定 (Config)
        "Gdrive_Asset_List_v2-10.xlsx.csv": CONFIG_DIR / "lora_assets.csv", # 実戦用名
        "Chronos_V3_Workflow.json": CONFIG_DIR / "workflow_api_template.json", # 器
        "system_prompt.txt": CONFIG_DIR / "system_prompt.txt",
    }

    # 3. 実行
    current_dir = Path(".")
    for src_name, dst_path in mapping.items():
        src_path = current_dir / src_name
        if src_path.exists():
            shutil.move(str(src_path), str(dst_path))
            print(f"✅ Integrated: {src_name} -> {dst_path.relative_to(BASE_DIR)}")

    # 4. 残ったファイルを legacy へ（整理を徹底）
    # ※特定の重要ファイル以外を legacy へ退避
    keep_dirs = [PROJECT_NAME, "workflows", "H-K9_Prompt_Engine"]
    for item in current_dir.iterdir():
        if item.name not in keep_dirs and item.name != "integrate_core.py":
            try:
                shutil.move(str(item), str(LEGACY_DIR / item.name))
            except: pass

    print(f"\n✨ 統合完了: {PROJECT_NAME} に全ての知性が集約されました。")

if __name__ == "__main__":
    organize_final()
