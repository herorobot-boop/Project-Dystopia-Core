import os
import subprocess
import shutil
from pathlib import Path

# =========================================================
# 1. 物理定数・認証情報の定義 (Genesis v7.5 Protocol)
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

# =========================================================
# 2. 執行フェーズ
# =========================================================

def main():
    print("🐺 [H-K9] 執行開始。手作業の時代を終わらせます。")

    # --- Step 1: Rclone 物理配線 ---
    print("📦 [1/5] Rclone 構成ファイルの自動注入...")
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)

    # --- Step 2: 兵站（モデル）の物理搬入 ---
    print("🚚 [2/5] Gdrive資産をNVMeへ爆速コピー中 (FUSE回避)...")
    model_dirs = ["checkpoints", "unet", "vlm", "loras"]
    for d in model_dirs:
        Path(f"/workspace/models/{d}").mkdir(parents=True, exist_ok=True)
    
    # size-only で既存ファイルを確認し、差分のみ高速コピー
    run_cmd("rclone copy gdrive:Project-Dystopia/models /workspace/models --progress --transfers 16 --size-only")

    # --- Step 3: 知能（GitHub）の同期 ---
    print("🧠 [3/5] GitHub 知能同期 (認証プロンプト排除)...")
    target_repo_path = "/workspace/Project-Dystopia-Core"
    if os.path.exists(target_repo_path):
        shutil.rmtree(target_repo_path)
    
    auth_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    run_cmd(f"git clone {auth_url} {target_repo_path}")

    # --- Step 4: 筋肉（Pip）の強制装着 ---
    print("💪 [4/5] 依存ライブラリの一括インストール...")
    os.chdir(target_repo_path)
    if os.path.exists("core/requirements.txt"):
        run_cmd("pip install -r core/requirements.txt")
    run_cmd("pip install llama-cpp-python huggingface_hub tqdm")

    # --- Step 5: Blackwell 点火構成の生成 ---
    print("🔥 [5/5] Blackwell 5090 最適化起動シーケンス生成...")
    # extra_model_paths.yaml の生成
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

    # --- 最終執行 ---
    print("\n✅ 全ての配線が完了しました。Blackwell を点火します。")
    os.chdir("/workspace/ComfyUI")
    # nvfp4 フラグを立てて起動
    run_cmd("python3 main.py --listen 0.0.0.0 --port 8188 --nvfp4 --bf16-storage --extra-model-paths-config " + str(yaml_file))

if __name__ == "__main__":
    main()
