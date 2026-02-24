import os
import subprocess
import shutil
from pathlib import Path

# =========================================================
# 1. 物理定数・認証情報
# =========================================================
GITHUB_TOKEN = "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"
GITHUB_REPO = "herorobot-boop/Project-Dystopia-Core"
RCLONE_CONF = """[gdrive]
type = drive
client_id = 449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com
client_secret = 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
scope = drive
token = {"access_token":"ya29.a0ATkoCc5QlctdSO6_EvRui6WBWvmadhFXUf5ivFmUJMUDjVym3tGw89E5JZfWLuYcLtpwN6bg5RmKBlQq86K0h9tupHGt9VdeizzVJjA53kJl3grbFl9HdGZxiE6ySXebJYoR2zKRiXl-lEsd8x4xgP45jbbCnrv3fOHWzn9EX1yjC7PijdM4YauAfavQvs_MraU64BsaCgYKAdQSARYSFQHGX2MiqS2BolCB1mOt2SO3Lx2j2w0206","token_type":"Bearer","refresh_token":"1//0eAe2MuCgFmXOCgYIARAAGA4SNwF-L9IrYBJhw7xOktAALZjz0ZRTVep-kwQOlDuPVSb5GQModG2t4rdVQWbmMWWJ2BBnVRZjZ5Y","expiry":"2026-02-24T18:00:37.5799933+09:00"}
"""

def run_cmd(cmd, shell=True):
    print(f"🚀 Executing: {cmd}")
    return subprocess.run(cmd, shell=shell, check=True)

def main():
    print("🐺 [H-K9] 執行開始。環境の欠落を補填し、点火します。")

    # --- Step 1: ComfyUI 本体の配備 ---
    comfy_path = Path("/workspace/ComfyUI")
    if not comfy_path.exists():
        print("🏗️ ComfyUI が見当たりません。新規建設を開始...")
        run_cmd(f"git clone https://github.com/comfyanonymous/ComfyUI.git {comfy_path}")
        # Managerも入れておくと後が楽です
        run_cmd(f"git clone https://github.com/ltdrdata/ComfyUI-Manager.git {comfy_path}/custom_nodes/ComfyUI-Manager")
        # ComfyUIの依存関係も解決
        run_cmd(f"pip install -r {comfy_path}/requirements.txt")

    # --- Step 2: Rclone & 兵站搬入 ---
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)
    
    for d in ["checkpoints", "unet", "vlm", "loras", "vae", "clip"]:
        Path(f"/workspace/models/{d}").mkdir(parents=True, exist_ok=True)
    
    run_cmd("rclone copy gdrive:Project-Dystopia/models /workspace/models --progress --transfers 16 --size-only")

    # --- Step 3: GitHub 知能同期 ---
    target_repo_path = "/workspace/Project-Dystopia-Core"
    if os.path.exists(target_repo_path):
        shutil.rmtree(target_repo_path)
    run_cmd(f"git clone https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git {target_repo_path}")

    # --- Step 4: 依存ライブラリの再装着 ---
    os.chdir(target_repo_path)
    run_cmd("pip install -r core/requirements.txt")
    run_cmd("pip install llama-cpp-python huggingface_hub tqdm")

    # --- Step 5: Blackwell 最適化設定 ---
    yaml_content = """comfyui:
    base_path: /workspace/models
    checkpoints: checkpoints/
    loras: loras/
    vae: vae/
    clip: clip/
    unet: unet/
"""
    yaml_file = Path(target_repo_path) / "core/protocols/extra_model_paths.yaml"
    yaml_file.parent.mkdir(parents=True, exist_ok=True)
    yaml_file.write_text(yaml_content)

    # --- 最終点火 ---
    print("\n✅ [H-K9] 基盤・知能・兵站、全て接続。Blackwell 点火。")
    os.chdir(comfy_path)
    run_cmd(f"python3 main.py --listen 0.0.0.0 --port 8188 --nvfp4 --bf16-storage --extra-model-paths-config {yaml_file}")

if __name__ == "__main__":
    main()
