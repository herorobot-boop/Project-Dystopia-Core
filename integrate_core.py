import os
import shutil
from pathlib import Path

# --- 設定 ---
PROJECT_NAME = "Project-Dystopia-Core"
ROOT = Path(".").resolve()
TARGET = ROOT / PROJECT_NAME
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
        "mutation_patterns.json", "mutation_scores.json" # 最新の変異関連を追加
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

# Legacy送りのキーワード（旧世代の残滓を確実に隔離）
LEGACY_KEYWORDS = [
    "PromptEngine", "setup_sync", "interface_gradio", "extract_frame", 
    "phase_v", "test_vlm", "H-K9_Core", "auto_transfer", "evaluate_log", 
    "execute_hk9", "io_utils", "morph_manager", "select_best_lora", 
    "cot_protocol", "h-k9_protocol", "vllm_config"
]

def ensure_dirs():
    """フォルダ構造をゼロから再構築"""
    for folder in STRUCTURE:
        (TARGET / folder).mkdir(parents=True, exist_ok=True)
    for sub in ["payload_logs", "images", "evolved_thoughts"]:
        (TARGET / "outputs" / sub).mkdir(parents=True, exist_ok=True)

def move_asset(src_name, dest_folder):
    """ルートからファイルを移動"""
    src = ROOT / src_name
    if src.exists():
        dest = TARGET / dest_folder / src.name
        shutil.move(str(src), str(dest))
        print(f"📁 Integrated: {src.name} → {dest_folder}/")

def recover_h_k9():
    """H-K9フォルダがある場合、中身を救出して統合"""
    if H_K9_DIR.exists():
        print("\n📡 Recovering assets from H-K9_Prompt_Engine...")
        # Config類
        for f in ["cot_protocol.txt", "llm_config.json", "lora_mapping.json", "scene_mapping.json", "system_prompt.txt"]:
            src = H_K9_DIR / f
            if src.exists():
                shutil.copy(str(src), str(TARGET / "config" / f))
        # Workflows
        old_wf = H_K9_DIR / "H-K9_Workflows"
        if old_wf.exists():
            for wf in old_wf.glob("*.json"):
                shutil.copy(str(wf), str(TARGET / "workflows" / wf.name))
        print("   └─ H-K9 assets have been merged.")

def cleanup_legacy():
    """ルートに残った不要な.pyやLegacyファイルを一掃"""
    for item in ROOT.glob("*"):
        if item.name in [PROJECT_NAME, "integrate_core.py", ".gitignore", "README.md", "requirements.txt", "H-K9_Prompt_Engine"]:
            continue
        if item.is_file() and (any(k in item.name for k in LEGACY_KEYWORDS) or item.suffix == ".py"):
            shutil.move(str(item), str(TARGET / "legacy" / item.name))
            print(f"🗃️ Legacy: {item.name} → legacy/")

def integrate():
    print("🧬 Finalizing Project-Dystopia-Core Infrastructure...\n")
    ensure_dirs()
    
    # 1. ルートの管理ファイルを移動
    for f in [".gitignore", "requirements.txt", "README.md"]:
        if (ROOT / f).exists():
            shutil.move(str(ROOT / f), str(TARGET / f))

    # 2. 定義された構成に沿って移動
    for folder, files in STRUCTURE.items():
        if folder in ["outputs", "legacy"]: continue
        for name in [f for f in files if (ROOT / f).exists()]:
            move_asset(name, folder)

    # 3. 特殊ディレクトリ処理
    recover_h_k9()
    cleanup_legacy()

    print(f"\n✅ All systems integrated into: {TARGET}")
    print("🚀 Ready for GitHub push or RunPod deployment.")

if __name__ == "__main__":
    integrate()
