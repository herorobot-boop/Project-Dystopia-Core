import os
import subprocess

# ---------------------------------------------------------
# フォルダ構成の定義 (マニュアル共有用)
# ---------------------------------------------------------
# /workspace/
# ├── models/               <- NVMe上の作業ディレクトリ (ComfyUIから参照)
# │   ├── checkpoints/
# │   ├── loras/
# │   └── vlm/
# ├── scripts/              <- この実行スクリプト
# └── logs/                 <- 転送ログ
# ---------------------------------------------------------

BASE_DIR = "/workspace"
MODEL_DIR = f"{BASE_DIR}/models"
LOG_DIR = f"{BASE_DIR}/logs"

def check_gpu():
    """GPUの種類を判別し、最適化設定を提案する"""
    result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=True, text=True)
    gpu_name = result.stdout.strip()
    print(f"Detected GPU: {gpu_name}")
    if "RTX 5090" in gpu_name:
        return "nvfp4"
    elif "H200" in gpu_name:
        return "bf16"
    return "fp8"

def sync_from_gdrive(remote_path, local_path):
    """Gdriveからの物理コピー。シンボリックリンク不可への回答"""
    print(f"Syncing {remote_path} to {local_path}...")
    # rclone copy を使用。整合性チェック(--checksum)を付与
    cmd = f"rclone copy {remote_path} {local_path} --progress --checksum --transfers 4"
    subprocess.run(cmd, shell=True)

def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    precision = check_gpu()
    
    # 1. 必要なディレクトリの作成
    dirs = ["checkpoints", "loras", "vlm", "unet", "vae"]
    for d in dirs:
        os.makedirs(os.path.join(MODEL_DIR, d), exist_ok=True)

    # 2. モデル転送 (Gdrive側のパスはHEROの設定に合わせる)
    # Z-Image, Wan 2.6 等の最新リスト
    sync_from_gdrive("gdrive:/ProjectDystopia/models/zimage", f"{MODEL_DIR}/checkpoints")
    sync_from_gdrive("gdrive:/ProjectDystopia/models/wan26", f"{MODEL_DIR}/unet")
    
    print(f"Setup Complete. Precision mode: {precision}")

if __name__ == "__main__":
    main()
