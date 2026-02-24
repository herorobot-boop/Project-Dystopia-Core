import os
import subprocess
import shutil
import time
from pathlib import Path

# =========================================================
# 物理定数・最新認証情報
# =========================================================
GITHUB_TOKEN = "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"
GITHUB_REPO = "herorobot-boop/Project-Dystopia-Core"

RCLONE_CONF = """[gdrive]
type = drive
client_id = 449525467106-qf2uaotmlk66di5cb6qbmj34iu04gv6b.apps.googleusercontent.com
client_secret = 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
scope = drive
token = {"access_token":"ya29.a0ATkoCc4U0Vl1S0oQxtpSHTTx_sxRHE9NkZO46Y8NKdFljt1ALjSEm5HJpggFxk8z0W-2l4TyZr0J-ttquDwRmanyTSDrHpGoBrahwQCkyOkPNRlTS3RdUQXIjwq-SDvR3s1UgjG42wMwUv6lRzeU7h2WMpGBWgzny1qO5CHjZd0F-ni_RPih-AsxpFFPBJx6JH5OirgaCgYKAZoSARYSFQHGX2MiDF9ygENm8NLx_BDOfs3X0w0206","token_type":"Bearer","refresh_token":"1//0eJk0XuWWbaYjCgYIARAAGA4SNwF-L9IrLfkJqCQZH2fvLNj9Oo7CaNyCifQqDtsoHBiP1VUpZiSGZeb2qWZXpqyIcsBhPFV_Ugc","expiry":"2026-02-24T19:54:56.1288591+09:00"}
"""

def run_cmd(cmd):
    print(f"🚀 Executing: {cmd}")
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def main():
    print("🐺 [H-K9] 最終制圧プロトコル発動。")

    # 1. 認証と配備 (Gdrive & GitHub)
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)

    comfy_path = "/workspace/ComfyUI"
    if not os.path.exists(comfy_path):
        run_cmd(f"git clone https://github.com/comfyanonymous/ComfyUI.git {comfy_path}")
        run_cmd(f"git clone https://github.com/ltdrdata/ComfyUI-Manager.git {comfy_path}/custom_nodes/ComfyUI-Manager")
        run_cmd(f"pip install -r {comfy_path}/requirements.txt")

    print("🚚 33GB資産の同期中...")
    run_cmd("rclone copy gdrive:Project-Dystopia/models /workspace/models --size-only")

    target_repo_path = "/workspace/Project-Dystopia-Core"
    if os.path.exists(target_repo_path): shutil.rmtree(target_repo_path)
    run_cmd(f"git clone https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git {target_repo_path}")
    run_cmd(f"pip install -r {target_repo_path}/core/requirements.txt")

    yaml_content = "comfyui:\n    base_path: /workspace/models\n    checkpoints: checkpoints/\n    loras: loras/\n    vae: vae/\n    clip: clip/\n    unet: unet/"
    yaml_file = Path(target_repo_path) / "core/protocols/extra_model_paths.yaml"
    yaml_file.write_text(yaml_content)

    # 2. ポート8888の解放とバックグラウンド点火
    print("🔥 最終工程：Jupyterをパージし、ComfyUIを永続化します...")
    
    # nohupでバックグラウンド実行し、ターミナルが切れても維持する
    launch_cmd = (
        f"nohup python3 {comfy_path}/main.py --listen 0.0.0.0 --port 8888 "
        f"--highvram --fp8_e4m3fn-unet --bf16-vae "
        f"--extra-model-paths-config {yaml_file} > /workspace/comfyui_starup.log 2>&1 &"
    )

    # Jupyterを殺す直前にコマンドを予約実行
    os.system(f"kill $(lsof -t -i:8888) && {launch_cmd}")
    
    print("\n✅ [H-K9] 完了！通信が切断されますが、正常です。")
    print("10秒後に RunPod の 'Jupyter Lab' リンクをクリックしてください。")

if __name__ == "__main__":
    main()
