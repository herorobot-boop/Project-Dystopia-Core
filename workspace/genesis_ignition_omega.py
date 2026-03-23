import os
import subprocess
import shutil
from pathlib import Path
import time

# =========================================================
# 🏛️ Project Dystopia: Genesis Ignition (Omega-Blackwell Ver.3)
# =========================================================
GITHUB_TOKEN = "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"
GITHUB_REPO = "herorobot-boop/Project-Dystopia-Core"

# 2026.03.24 最新の認証トークンを内蔵
RCLONE_CONF = """[gdrive]
type = drive
client_id = 449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com
client_secret = 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
scope = drive
token = {"access_token":"ya29.a0ATkoCc5uPfwemGWNxdcG7WP207hUl_unvldyPhKTmqmDO2MF0mAIQ9ojXP5RhaEZcNXOeeqLqJCgcbaTxJSy4PVA9Dr_Ky415655WrEf9c_h87ueX2GFrIl1x_e8guC5Ef6LcbXu7tOThm9BhJi96CQH_sEkUlmZP_Bn4X6E45_DqI3lkQZahLwwlEIUxjMtNnb9L2IaCgYKAc4SARYSFQHGX2MizMKudkfZnY17qJuQWMFI1g0206","token_type":"Bearer","refresh_token":"1//0ehxqw9InG0QACgYIARAAGA4SNwF-L9IrhALZhzaQ_5BKHaAK4LVoaAjIipQQxc_SbVZxthIUuNY23-z4xR26SKTdwJkcev2Ind0","expiry":"2026-03-24T12:58:51Z"}
"""

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, executable='/bin/bash')
    if res.returncode != 0:
        print(f"⚠️ Warning: Command failed -> {cmd}")

def setup_omega():
    print("🐺 [H-K9] 最終兵装 Qwen3.5-IQ4_XS & Blackwell 5090 交互覚醒シークエンス点火。")

    # --- Step 1: 基礎インフラの徴用 ---
    run_cmd("apt-get update && apt-get install -y rclone tmux fuser zstd")
    # Blackwell 最適化版 Llama-cpp (CUDA 12.x 対応) をビルドインストール
    run_cmd("CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python gguf sage-attention requests websocket-client")

    # --- Step 2: 兵站（モデル）の zstd 高速展開 ---
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)

    # 5090 領土の作成
    os.makedirs("/workspace/models/vlm", exist_ok=True)
    os.makedirs("/workspace/models/unet", exist_ok=True)
    os.makedirs("/workspace/models/checkpoints", exist_ok=True)

    print("🚚 [Logistics] Ver.3 zstd プロトコルによる高速搬入...")
    # Gdrive 上に事前作成した圧縮アーカイブを 1 本のみ取得 (I/O オーバーヘッド抹殺)
    run_cmd("rclone copy gdrive:Project_Dystopia/Dystopia_Assets.tar.zst /workspace/ --progress")
    
    print("📦 [Extract] NVMe 上で資産を瞬間展開...")
    run_cmd("tar -I zstd -xf /workspace/Dystopia_Assets.tar.zst -C /workspace/")
    run_cmd("rm /workspace/Dystopia_Assets.tar.zst")

    # --- Step 3: 司令塔（GitHub）との神経接続 ---
    auth_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    run_cmd(f"rm -rf /workspace/Project-Dystopia-Core && git clone {auth_url} /workspace/Project-Dystopia-Core")

    # --- Step 4: 5090 Blackwell 司令室起動 ---
    # ポート 8888 を Jupyter から奪還
    run_cmd("fuser -k 8888/tcp || true")
    time.sleep(2)

    # tmux セッション構築
    # 左: ComfyUI (Wan 2.2 Turbo 専用 / --nvfp4 適用)
    # 右: Main_Omega.py (Qwen 3.5 IQ4_XS 思考・スワップ制御)
    launch_cmd = (
        "tmux new-session -d -s h_k9_omega 'cd /workspace/ComfyUI && "
        "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True && "
        "python3 main.py --listen 0.0.0.0 --port 8888 --nvfp4 --bf16-storage --weight-streaming "
        "--extra-model-paths-config /workspace/Project-Dystopia-Core/core/protocols/extra_model_paths.yaml'; "
        "tmux split-window -h -t h_k9_omega 'cd /workspace/Project-Dystopia-Core && python3 Main_Omega.py'; "
        "tmux attach-session -t h_k9_omega"
    )
    
    print("🏁 [Ready] 司令官、全ての神経接続が完了しました。tmux 司令室へ移行します。")
    os.system(launch_cmd)

if __name__ == "__main__":
    setup_omega()
