import os
import subprocess
from pathlib import Path
import time

# =========================================================
# 🏛️ 物理定数・認証情報の最終同期
# =========================================================
GITHUB_TOKEN = "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"
GITHUB_REPO = "herorobot-boop/Project-Dystopia-Core"

# ★重要：NotebookLMが指摘した「最新のtoken」を含む完全なRCLONE_CONF
RCLONE_CONF = """[gdrive]
type = drive
client_id = 449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com
client_secret = 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
scope = drive
token = {"access_token":"ya29.a0ATkoCc4U0Vl1S0oQxtpSHTTx_sxRHE9NkZO46Y8NKdFljt1ALjSEm5HJpggFxk8z0W-2l4TyZr0J-ttquDwRmanyTSDrHpGoBrahwQCkyOkPNRlTS3RdUQXIjwq-SDvR3s1UgjG42wMwUv6lRzeU7h2WMpGBWgzny1qO5CHjZd0F-ni_RPih-AsxpFFPBJx6JH5OirgaCgYKAZoSARYSFQHGX2MiDF9ygENm8NLx_BDOfs3X0w0206","token_type":"Bearer","refresh_token":"1//0eJk0XuWWbaYjCgYIARAAGA4SNwF-L9IrLfkJqCQZH2fvLNj9Oo7CaNyCifQqDtsoHBiP1VUpZiSGZeb2qWZXpqyIcsBhPFV_Ugc","expiry":"2026-02-24T19:54:56.1288591+09:00"}
"""

def run_cmd(cmd):
    print(f"📡 Executing: {cmd}")
    subprocess.run(cmd, shell=True, executable='/bin/bash')

def setup_dystopia():
    print("🐺 [H-K9] 最終制圧シーケンス：オメガ・ブラックウェル点火。")

    # 1. 依存関係の浄化と徴用
    run_cmd("apt-get update && apt-get install -y rclone tmux fuser lsof")
    run_cmd("pip install llama-cpp-python gguf sage-attention requests websocket-client")

    # 2. 兵站の搬入 (Gdrive -> NVMe 物理コピー)
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)

    # 5090の領土（ディレクトリ）作成
    os.makedirs("/workspace/models/unet", exist_ok=True)
    os.makedirs("/workspace/models/vlm", exist_ok=True)
    os.makedirs("/workspace/models/checkpoints", exist_ok=True)

    print("🚚 33GBの資産を着弾させます（Wan 2.2 / Qwen3.5）...")
    # 既存ファイルがあればスキップして高速化
    run_cmd("rclone copy gdrive:Project-Dystopia/models/wan22 /workspace/models/unet --size-only -P")
    run_cmd("rclone copy gdrive:Project-Dystopia/models/vlm /workspace/models/vlm --size-only -P")

    # 3. 司令塔（知能層）の同期
    auth_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    run_cmd(f"rm -rf /workspace/Project-Dystopia-Core && git clone {auth_url} /workspace/Project-Dystopia-Core")

    # 4. 点火用 YAML 生成
    yaml_content = """comfyui:
    base_path: /workspace/models
    unet: unet/
    vlm: vlm/
    checkpoints: checkpoints/
    loras: loras/
"""
    Path("/workspace/ComfyUI/extra_model_paths.yaml").write_text(yaml_content)

    # 5. Jupyter パージ (Port 8888 奪取)
    run_cmd("fuser -k 8888/tcp || true")
    time.sleep(2)

    # 6. Blackwell 5090 司令室 (tmux) の構築
    # 左パネル: ComfyUI (nvfp4 / weight-streaming / VRAM最適化環境変数)
    # 右パネル: Main.py (聖典入力インターフェース)
    launch_cmd = (
        "tmux new-session -d -s h_k9 'cd /workspace/ComfyUI && "
        "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True && "
        "python3 main.py --listen 0.0.0.0 --port 8888 --nvfp4 --bf16-storage --weight-streaming "
        "--extra-model-paths-config extra_model_paths.yaml'; "
        "tmux split-window -h -t h_k9 'cd /workspace/Project-Dystopia-Core && python3 Main.py'; "
        "tmux attach-session -t h_k9"
    )
    
    print("\n✅ [H-K9] 全神経接続完了。tmux 司令室へ移行します。")
    os.system(launch_cmd)

if __name__ == "__main__":
    setup_dystopia()
