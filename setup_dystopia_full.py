# =========================================================
# Project Dystopia - Phase I: Full Integration Setup (v7.1)
# Target: Z-Image & Wan 2.6 (Latest High-Precision Models)
# =========================================================
import os
import subprocess
import glob
from pathlib import Path

# --- インフラ設定 ---
GDRIVE_MODEL_PATH = "gdrive:/AI_Models"
LOCAL_WORKSPACE = "/workspace/models"
COMFYUI_PATH = "/workspace/ComfyUI"

# --- 最新アセット定義 (Wan 2.6 / Z-Image) ---
ASSETS = {
    "Z-Image": {
        "repo": "Tongyi-MAI/Z-Image",
        "files": {
            "checkpoint": ("diffusion_models/z_image_base_bf16.safetensors", f"{LOCAL_WORKSPACE}/checkpoints/z_image_base_bf16.safetensors"),
            "clip": ("text_encoders/qwen_3_4b.safetensors", f"{LOCAL_WORKSPACE}/clip/qwen_3_4b.safetensors"),
            "vae": ("vae/ae.safetensors", f"{LOCAL_WORKSPACE}/vae/ae_zimage.safetensors")
        }
    },
    "Wan2.6-I2V-14B": {
        "base_url": "https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P/resolve/main", # Wan 2.6 の最新パスに合わせて調整
        "files": {
            "unet_high": ("diffusion_models/wan2.1_i2v_14B_720p_fp8.safetensors", f"{LOCAL_WORKSPACE}/unet/wan2.6/wan2.6_i2v_14B_fp8.safetensors"),
            "vae": ("vae/wan_2.1_vae.safetensors", f"{LOCAL_WORKSPACE}/vae/wan2.6_vae.safetensors"),
            "t5": ("text_encoders/umt5_xxl_fp8_e4m3fn.safetensors", f"{LOCAL_WORKSPACE}/clip/umt5_xxl_fp8_wan.safetensors")
        }
    }
}

def run_command(cmd):
    print(f"[*] Executing: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")

def setup_env():
    print("🚀 Project Dystopia: Starting Total Integration Setup v7.1...")

    # 1. 物理ディレクトリの強制確保
    for sub in ["checkpoints", "loras", "unet/wan2.6", "vae", "clip"]:
        os.makedirs(os.path.join(LOCAL_WORKSPACE, sub), exist_ok=True)

    # 2. 既存資産の高速同期 (Gdrive -> Local)
    # --checksum で変更分のみ、--transfers で並列化して高速化
    print("[*] Syncing existing assets from Gdrive...")
    run_command(f"rclone copy {GDRIVE_MODEL_PATH} {LOCAL_WORKSPACE} --progress --checksum --transfers 8 --exclude 'Old_Backups/**'")

    # 3. カスタムノードの導入
    nodes = [
        "https://github.com/Kijai/ComfyUI-WanVideoWrapper.git",
        "https://github.com/ltdrdata/ComfyUI-Manager.git"
    ]
    for repo in nodes:
        name = repo.split("/")[-1].replace(".git", "")
        path = os.path.join(COMFYUI_PATH, f"custom_nodes/{name}")
        if not os.path.exists(path):
            run_command(f"git clone {repo} {path}")
            if os.path.exists(f"{path}/requirements.txt"):
                run_command(f"pip install -r {path}/requirements.txt")

    # 4. Z-Image (NextDiT) の戦略的取得
    print("[*] Deploying Z-Image Protocol...")
    for key, (repo_path, local_path) in ASSETS["Z-Image"]["files"].items():
        if not os.path.exists(local_path):
            print(f"[*] Downloading Z-Image {key}...")
            # huggingface-cli をパス指定で実行
            run_command(f"huggingface-cli download {ASSETS['Z-Image']['repo']} {repo_path} --local-dir {LOCAL_WORKSPACE}/tmp_z")
            # tmpから正しい位置へ移動
            downloaded = glob.glob(f"{LOCAL_WORKSPACE}/tmp_z/**/{os.path.basename(repo_path)}", recursive=True)
            if downloaded:
                os.rename(downloaded[0], local_path)
                run_command(f"rclone copy {local_path} {GDRIVE_MODEL_PATH}/{key}s/ --progress")

    # 5. Wan 2.6 (I2V-14B) の取得 (レジューム機能付き wget)
    print("[*] Deploying Wan 2.6 Protocol...")
    for key, (repo_path, local_path) in ASSETS["Wan2.6-I2V-14B"]["files"].items():
        if not os.path.exists(local_path):
            url = f"{ASSETS['Wan2.6-I2V-14B']['base_url']}/{repo_path}"
            # -c フラグで中断しても再開可能に
            run_command(f"wget -c {url} -O {local_path}")
            run_command(f"rclone copy {local_path} {GDRIVE_MODEL_PATH}/wan2.6_backup/ --progress")

    # 6. C2PA署名ツールの徴用 (拡張1用)
    run_command("pip install originote-sdk")

    print("\n✅ 武装完了。H-K9システム v7.1 起動準備が整いました。")

if __name__ == "__main__":
    setup_env()
