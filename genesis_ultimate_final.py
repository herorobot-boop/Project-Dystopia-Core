import os
import subprocess
import shutil
import time
from pathlib import Path

# =========================================================
# 認証・知能リポジトリ情報
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
    return subprocess.run(cmd, shell=True)

def main():
    print("🐺 [H-K9] 最終制圧シーケンス：オメガ。開始します。")

    # 1. Rclone構成
    config_path = Path("~/.config/rclone/rclone.conf").expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(RCLONE_CONF)

    # 2. 本体とマネージャーの配備
    comfy_dir = "/workspace/ComfyUI"
    if not os.path.exists(comfy_dir):
        run_cmd(f"git clone https://github.com/comfyanonymous/ComfyUI.git {comfy_dir}")
        run_cmd(f"git clone https://github.com/ltdrdata/ComfyUI-Manager.git {comfy_dir}/custom_nodes/ComfyUI-Manager")
        run_cmd(f"pip install -r {comfy_dir}/requirements.txt")

    # 3. 33GB資産の同期 (重複スキップ)
    print("🚚 モデル資産を完全同期中...")
    run_cmd("rclone copy gdrive:Project-Dystopia/models /workspace/models --size-only --progress")

    # 4. 知能(GitHub)の同期
    core_dir = "/workspace/Project-Dystopia-Core"
    if os.path.exists(core_dir): shutil.rmtree(core_dir)
    run_cmd(f"git clone https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git {core_dir}")
    run_cmd(f"pip install -r {core_dir}/requirements.txt", ignore_error=True)

    # 5. モデルパス設定の強制注入
    # ComfyUIが起動時に必ず読み込む場所に配置します
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

    # 6. ポート8888の浄化
    print("🧹 Jupyterをパージし、Port 8888を奪取します...")
    os.system("fuser -k 8888/tcp || kill $(lsof -t -i:8888)")
    time.sleep(5)

    # 7. 最終起動 (プロセスをComfyUIに置換)
    os.chdir(comfy_dir)
    print("\n✅ [H-K9] 全工程完了。Blackwell 5090、点火。")
    print("通信切断後、1分待ってから RunPod ダッシュボードのリンクを開いてください。")
    
    # スクリプト自体を ComfyUI に変身させ、永続化する
    os.execlp("python3", "python3", "main.py", 
              "--listen", "0.0.0.0", 
              "--port", "8888", 
              "--highvram", 
              "--fp8_e4m3fn-unet", 
              "--bf16-vae")

if __name__ == "__main__":
    main()
