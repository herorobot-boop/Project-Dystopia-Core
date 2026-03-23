import os
import subprocess
import shutil
from pathlib import Path
import time

# =========================================================
# 🏛️ Project Dystopia: Genesis Ultimate Final (Omega-Blackwell)
# =========================================================
GITHUB_TOKEN = "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"
GITHUB_REPO = "herorobot-boop/Project-Dystopia-Core"

# NotebookLMが特定した最新の認証情報
RCLONE_CONF = """[gdrive]
type = drive
client_id = 449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com
client_secret = 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
scope = drive
token = {"access_token":"ya29.a0ATkoCc5uPfwemGWNxdcG7WP207hUl_unvldyPhKTmqmDO2MF0mAIQ9ojXP5RhaEZcNXOeeqLqJCgcbaTxJSy4PVA9Dr_Ky415655WrEf9c_h87ueX2GFrIl1x_e8guC5Ef6LcbXu7tOThm9BhJi96CQH_sEkUlmZP_Bn4X6E45_DqI3lkQZahLwwlEIUxjMtNnb9L2IaCgYKAc4SARYSFQHGX2MizMKudkfZnY17qJuQWMFI1g0206","token_type":"Bearer","refresh_token":"1//0ehxqw9InG0QACgYIARAAGA4SNwF-L9IrhALZhzaQ_5BKHaAK4LVoaAjIipQQxc_SbVZxthIUuNY23-z4xR26SKTdwJkcev2Ind0","expiry":"2026-03-24T12:58:51Z"}
"""

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    subprocess.run(cmd, shell=True, executable='/bin/bash')

def setup_dystopia():
    print("🐺 [H-K9] 最終制圧シーケンス：オメガ・ブラックウェル点火。")

    # 1. 依存関係の浄化と徴用
    run_cmd("apt-get update && apt-get install -y rclone tmux fuser lsof tar zstd")
    run_cmd("CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python gguf sage-attention requests websocket-client pandas")

    # 2. 兵站の搬入 (Gdrive -> NVMe 物理コピー) [3, 4]
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)

    os.makedirs("/workspace/models/unet", exist_ok=True)
    os.makedirs("/workspace/models/vlm", exist_ok=True)
    os.makedirs("/workspace/models/checkpoints", exist_ok=True)

    print("🚚 兵站：最新モデルを直接射出（Qwen3.5 IQ4_XS & Wan 2.2）...")
    # Hugging Faceからの直送プロトコル [5]
    run_cmd("rclone copyurl 'https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf' gdrive:Project_Dystopia/Models/VLM/ --progress")
    run_cmd("rclone copyurl 'https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/mmproj-Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-f16.gguf' gdrive:Project_Dystopia/Models/VLM/ --progress")
    
    # GdriveからNVMeへ物理同期（FUSEエラー回避） [6]
    run_cmd("rclone copy gdrive:Project_Dystopia/Models /workspace/models --size-only -P --transfers 8")

    # 3. 司令塔（知能層）の同期
    auth_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    run_cmd(f"rm -rf /workspace/Project-Dystopia-Core && git clone {auth_url} /workspace/Project-Dystopia-Core")

    # 4. 点火用 YAML 生成 [7, 8]
    yaml_content = """comfyui:
    base_path: /workspace/models
    checkpoints: checkpoints/
    clip: clip/
    unet: unet/
    vlm: vlm/
    loras: loras/
"""
    Path("/workspace/ComfyUI/extra_model_paths.yaml").write_text(yaml_content)

    # 5. Jupyter パージ (Port 8888 奪取) [9]
    run_cmd("fuser -k 8888/tcp || true")
    time.sleep(5) # 浄化待機

    # 6. Blackwell 5090 司令室 (tmux) の構築 [1, 10]
    # 左パネル: ComfyUI (nvfp4 / weight-streaming / VRAM最適化)
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
