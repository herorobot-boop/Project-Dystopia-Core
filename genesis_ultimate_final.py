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

    # 1. 基礎インフラと 5090 最適化ビルド
    run_cmd("apt-get update && apt-get install -y rclone tmux fuser lsof tar zstd wget git")
    run_cmd("pip install --upgrade pip")
    run_cmd("CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python gguf sage-attention requests websocket-client pandas pillow")

    # 2. 兵站搬入プロトコル
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)

    vlm_path = "/workspace/models/vlm"
    os.makedirs(vlm_path, exist_ok=True)
    os.makedirs("/workspace/models/unet", exist_ok=True)
    os.makedirs("/workspace/models/checkpoints", exist_ok=True)

    print("🚚 兵站：最新モデル（Qwen3.5 IQ4_XS & Wan 2.2）を射出...")
    hf_base = "https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/"
    hf_models = [
        "Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf",
        "mmproj-Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-f16.gguf"
    ]
    for m in hf_models:
        if not os.path.exists(f"{vlm_path}/{m}"):
            run_cmd(f"wget -c {hf_base}{m} -P {vlm_path}/")

    run_cmd("rclone copy gdrive:Project_Dystopia/Models /workspace/models --size-only -P --transfers 8")

    # 3. 司令塔同期
    auth_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    run_cmd(f"rm -rf /workspace/Project-Dystopia-Core && git clone {auth_url} /workspace/Project-Dystopia-Core")

    # 4. ComfyUI パス定義
    yaml_content = """comfyui:
    base_path: /workspace/models
    checkpoints: checkpoints/
    clip: clip/
    unet: unet/
    vlm: vlm/
    loras: loras/
"""
    Path("/workspace/ComfyUI/extra_model_paths.yaml").write_text(yaml_content)

    # 5. ポート浄化
    run_cmd("fuser -k 8888/tcp || true")
    time.sleep(3) 

    # 6. tmux 司令室（h_k9）展開
    launch_cmd = (
        "tmux new-session -d -s h_k9 'cd /workspace/ComfyUI && "
        "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True && "
        "python3 main.py --listen 0.0.0.0 --port 8888 --nvfp4 --bf16-storage --weight-streaming "
        "--extra-model-paths-config extra_model_paths.yaml'; "
        "tmux split-window -h -t h_k9 'cd /workspace/Project-Dystopia-Core && python3 Main.py'; "
        "tmux attach-session -t h_k9"
    )

    print("\n✅ [H-K9] 神経接続完了。tmux セッション 'h_k9' を確認してください。")
    os.system(launch_cmd)

if __name__ == "__main__":
    setup_dystopia()
