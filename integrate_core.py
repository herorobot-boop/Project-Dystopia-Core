import os
import shutil
from pathlib import Path

# --- 設定 ---
ROOT = Path(".").resolve()
TARGET = ROOT / "Project-Dystopia-Core"
H_K9_DIR = ROOT / "H-K9_Prompt_Engine"

# ディレクトリ構成定義
STRUCTURE = {
    "core": [
        "thought_generator.py", "lora_selector.py", "prompt_builder.py",
        "prompt_to_comfy.py", "workflow_mapper.py", "run_batch.py",
        "run_evolved_batch.py", "result_watcher.py", "score_thoughts.py",
        "evaluator.py", "evolution_tracker.py", "mutation_lab.py",
        "bloodline_viewer.py"
    ],
    "config": [
        "workflow_api_template.json", "lora_assets.csv", "system_prompt.txt",
        "llm_config.json", "lora_mapping.json", "scene_mapping.json",
        "structure_tags.json", "realism_logic.json", "mapping_config.json",
        "mutation_patterns.json"
    ],
    "workflows": [
        "Type-A.json", "Type-B.json", "Type-C.json",
        "Type-D.json", "Type-D+.json", "Type-E.json",
        "Workflow-F.json", "Workflow-F+.json"
    ],
    "outputs": [
        "payload_logs", "images", "evolved_thoughts", "thought_log.jsonl"
    ],
    "legacy": []
}

# Legacy送りのキーワード
LEGACY_KEYWORDS = [
    "PromptEngine", "setup_sync", "interface_gradio", "extract_frame", 
    "phase_v", "test_vlm", "H-K9_Core", "auto_transfer", "evaluate_log", 
    "execute_hk9", "io_utils", "morph_manager", "select_best_lora", 
    "cot_protocol", "h-k9_protocol", "vllm_config"
]

def ensure_dirs():
    """必要な全ディレクトリを作成"""
    for folder in STRUCTURE:
        (TARGET / folder).mkdir(parents=True, exist_ok=True)
    # outputのサブディレクトリを強制作成
    for sub in ["payload_logs", "images", "evolved_thoughts"]:
        (TARGET / "outputs" / sub).mkdir(parents=True, exist_ok=True)

def move_file(src_name, dest_folder):
    """ファイルを指定フォルダへ移動（ルートから）"""
    src = ROOT / src_name
    if src.exists():
        dest = TARGET / dest_folder / src.name
        shutil.move(str(src), str(dest))
        print(f"📁 Moved: {src.name} → {dest_folder}/")

def move_h_k9_assets():
    """H-K9_Prompt_Engineフォルダから資産を救出"""
    if H_K9_DIR.exists():
        print("\n📡 Recovering assets from H-K9_Prompt_Engine...")
        # Config関連の救出
        config_targets = ["cot_protocol.txt", "llm_config.json", "lora_mapping.json", 
                          "scene_mapping.json", "system_prompt.txt"]
        for target in config_targets:
            src = H_K9_DIR / target
            if src.exists():
                shutil.copy(str(src), str(TARGET / "config" / target))
                print(f"   └─ {target} → config/")
        
        # 旧Workflowの救出
        old_wf_dir = H_K9_DIR / "H-K9_Workflows"
        if old_wf_dir.exists():
            for wf in old_wf_dir.glob("*.json"):
                shutil.copy(str(wf), str(TARGET / "workflows" / wf.name))
                print(f"   └─ {wf.name} → workflows/")

def move_outputs():
    """既存の出力データやログを移動"""
    for item in STRUCTURE["outputs"]:
        src = ROOT / item
        if src.exists():
            dest = TARGET / "outputs" / src.name
            if src.is_dir():
                # フォルダの中身をマージ
                for f in src.glob("*"):
                    shutil.move(str(f), str(dest / f.name))
            else:
                shutil.move(str(src), str(dest))
            print(f"📦 Output matched: {src.name} → outputs/")

def move_legacy():
    """過去の遺産をlegacyへ退避"""
    for file in ROOT.glob("*"):
        # 既に整理済みのフォルダや重要な管理ファイルは除外
        if item_is_protected(file):
            continue
        
        if any(key in file.name for key in LEGACY_KEYWORDS) or file.suffix == ".py":
            dest = TARGET / "legacy" / file.name
            shutil.move(str(file), str(dest))
            print(f"🗃️ Legacy: {file.name} → legacy/")

def item_is_protected(path):
    protected = [PROJECT_NAME, "integrate_core.py", ".gitignore", "README.md", "requirements.txt", "H-K9_Prompt_Engine"]
    return path.name in protected or path.is_dir() and path.name == "Project-Dystopia-Core"

def integrate():
    print("🧬 Starting Project Dystopia Core: Final Defense Line Integration...\n")
    ensure_dirs()

    # Metaファイルの移動
    for meta in [".gitignore", "requirements.txt", "README.md"]:
        if (ROOT / meta).exists():
            shutil.move(str(ROOT / meta), str(TARGET / meta))
            print(f"🛡️ Meta: {meta} → ROOT/")

    # 各ディレクトリへの仕分け
    for folder, files in STRUCTURE.items():
        if folder in ["outputs", "legacy"]: continue
        for name in files:
            move_file(name, folder)

    move_outputs()
    move_h_k9_assets()
    move_legacy()

    print(f"\n✅ Integration complete. Your 'Project-Dystopia-Core' is now a unified intelligence.")

if __name__ == "__main__":
    integrate()
