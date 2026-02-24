import os
import subprocess
import shutil
import time
from pathlib import Path

# =========================================================
# 認証・リポジトリ設定
# =========================================================
GITHUB_TOKEN = "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"
GITHUB_REPO = "herorobot-boop/Project-Dystopia-Core"

def run_cmd(cmd):
    print(f"🚀 Executing: {cmd}")
    return subprocess.run(cmd, shell=True)

def main():
    print("🐺 [H-K9] 最終制圧プロトコル Ver.3 改動。")

    # 1. 物理的な場所を空ける
    print("🧹 ポート 8888 を完全に浄化します...")
    os.system("fuser -k 8888/tcp || kill $(lsof -t -i:8888)")
    time.sleep(5)  # ポートが完全に解放されるまで待機

    # 2. パス設定 (ComfyUI 直下に配置することで強制認識させる)
    comfy_dir = "/workspace/ComfyUI"
    yaml_dest = f"{comfy_dir}/extra_model_paths.yaml"
    
    yaml_content = """comfyui:
    base_path: /workspace/models
    checkpoints: checkpoints/
    loras: loras/
    vae: vae/
    clip: clip/
    unet: unet/
"""
    with open(yaml_dest, "w") as f:
        f.write(yaml_content)
    print(f"📄 設定ファイルを配置: {yaml_dest}")

    # 3. 起動コマンド (nohupを使わず、このスクリプトを「親」として維持)
    # これにより、ターミナルが切れてもOSがプロセスを保護します
    os.chdir(comfy_dir)
    cmd = (
        "python3 main.py --listen 0.0.0.0 --port 8888 "
        "--highvram --fp8_e4m3fn-unet --bf16-vae"
    )

    print("\n🔥 [Blackwell 5090] 本点火。")
    print("この後、接続が切れますが、1分後にブラウザで 8888 リンクを開いてください。")
    
    # 最後にこのプロセス自体が ComfyUI に「変身」する
    os.execlp("python3", "python3", "main.py", "--listen", "0.0.0.0", "--port", "8888", "--highvram", "--fp8_e4m3fn-unet", "--bf16-vae")

if __name__ == "__main__":
    main()
