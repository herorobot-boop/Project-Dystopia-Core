import os
import subprocess
import time
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis Ignition (Omega-Blackwell)
# =========================================================
RCLONE_CONF = """[gdrive]
type = drive
client_id = 449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com
client_secret = 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
scope = drive
token = {"access_token":"ya29.a0ATkoCc5uPfwemGWNxdcG7WP207hUl_unvldyPhKTmqmDO2MF0mAIQ9ojXP5RhaEZcNXOeeqLqJCgcbaTxJSy4PVA9Dr_Ky415655WrEf9c_h87ueX2GFrIl1x_e8guC5Ef6LcbXu7tOThm9BhJi96CQH_sEkUlmZP_Bn4X6E45_DqI3lkQZahLwwlEIUxjMtNnb9L2IaCgYKAc4SARYSFQHGX2MizMKudkfZnY17qJuQWMFI1g0206","token_type":"Bearer","refresh_token":"1//0ehxqw9InG0QACgYIARAAGA4SNwF-L9IrhALZhzaQ_5BKHaAK4LVoaAjIipQQxc_SbVZxthIUuNY23-z4xR26SKTdwJkcev2Ind0","expiry":"2026-03-24T12:58:51Z"}
"""

def setup_dystopia():
    print("🐺 [H-K9] 物理層浄化およびオメガ・点火シークエンス開始。")
    
    # 1. 依存関係の徴用 (zstd, rclone, tmux)
    os.system("apt-get update && apt-get install -y rclone tmux fuser zstd")
    os.system("CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python gguf sage-attention requests websocket-client")

    # 2. 兵站：GdriveからNVMeへの一本背負い (zstd) 搬入
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)
    
    # Gdrive上のアーカイブ(Dystopia_Assets.tar.zst)を落として展開
    os.makedirs("/workspace/models", exist_ok=True)
    print("🚚 33GBの軍需物資を高速搬入中 (zstd 6分プロトコル)...")
    os.system("rclone copy gdrive:Project-Dystopia/Dystopia_Assets.tar.zst /workspace/ --progress")
    os.system("tar -I zstd -xf /workspace/Dystopia_Assets.tar.zst -C /workspace/models")

    # 3. 司令塔 (GitHub) 同期
    token = "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"
    os.system(f"rm -rf /workspace/Project-Dystopia-Core && git clone https://{token}@github.com/herorobot-boop/Project-Dystopia-Core.git /workspace/Project-Dystopia-Core")

    # 4. ポート8888の浄化待機
    os.system("fuser -k 8888/tcp || true")
    time.sleep(5)

    # 5. Blackwell 5090 司令室の左右分割展開 (tmux)
    launch_cmd = (
        "tmux new-session -d -s h_k9 'cd /workspace/ComfyUI && "
        "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True && "
        "python3 main.py --listen 0.0.0.0 --port 8888 --nvfp4 --bf16-storage --weight-streaming'; "
        "tmux split-window -h -t h_k9 'cd /workspace/Project-Dystopia-Core && python3 Main.py'; "
        "tmux attach-session -t h_k9"
    )
    os.system(launch_cmd)

if __name__ == "__main__":
    setup_dystopia()
