# =========================================================
# Project Dystopia - Phase I: Full Integration Setup (v7.2)
# Target: Wan 2.2 (I2V-14B) & Z-Image [Fast Sync Mode]
# =========================================================
import os
import subprocess
import glob
from pathlib import Path

# --- インフラ設定 ---
GDRIVE_MODEL_PATH = "gdrive:/AI_Models"
LOCAL_WORKSPACE = "/workspace/models"
COMFYUI_PATH = "/workspace/ComfyUI"

# --- 最新アセット定義 (Wan 2.2 14B / Z-Image) ---
ASSETS = {
    "Z-Image": {
        "repo": "Tongyi-MAI/Z-Image",
        "files": {
            "checkpoint": ("diffusion_models/z_image_base_bf16.safetensors", f"{LOCAL_WORKSPACE}/checkpoints/z_image_base_bf16.safetensors"),
            "clip": ("text_encoders/qwen_3_4b.safetensors", f"{LOCAL_WORKSPACE}/clip/qwen_3_4b.safetensors"),
            "vae": ("vae/ae.safetensors", f"{LOCAL_WORKSPACE}/vae/ae_zimage.safetensors")
        }
    },
    "Wan2.2-I2V-14B": {
        "base_url": "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files",
        "files": {
            "unet": ("diffusion_models/wan2.2_i2v_14B_fp8.safetensors", f"{LOCAL_WORKSPACE}/unet/wan2.2/wan2.2_i2v_14B_fp8.safetensors"),
            "vae": ("vae/wan2.2_vae.safetensors", f"{LOCAL_WORKSPACE}/vae/wan2.2_vae.safetensors"),
            "t5": ("text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", f"{LOCAL_WORKSPACE}/clip/umt5_xxl_fp8.safetensors")
        }
    }
}

def run_command(cmd):
    print(f"[*] Executing: {cmd}")
    subprocess.run(cmd, shell=True)

def setup_env():
    print("🚀 Project Dystopia: Starting Total Integration Setup v7.2...")

    # 1. 物理ディレクトリの強制確保
    for sub in ["checkpoints", "loras", "unet/wan2.2", "vae", "clip"]:
        os.makedirs(os.path.join(LOCAL_WORKSPACE, sub), exist_ok=True)

    # 2. 高速同期（Fast Sync）
    # すでにファイルがある場合はハッシュ計算をせず、サイズと時間のみで同期
    print("[*] Synchronizing Gdrive assets (Fast Mode)...")
    run_command(f"rclone copy {GDRIVE_MODEL_PATH} {LOCAL_WORKSPACE} --progress --update --size-only --transfers 16")

    # 3. カスタムノードの導入 (Wan 2.2 Wrapper)
    wrapper_path = os.path.join(COMFYUI_PATH, "custom_nodes/ComfyUI-WanVideoWrapper")
    if not os.path.exists(wrapper_path):
        run_command(f"git clone https://github.com/Kijai/ComfyUI-WanVideoWrapper.git {wrapper_path}")
        run_command(f"pip install -r {wrapper_path}/requirements.txt")

    # 4. Z-Image 取得
    for key, (repo_path, local_path) in ASSETS["Z-Image"]["files"].items():
        if not os.path.exists(local_path):
            print(f"[*] Downloading Z-Image {key}...")
            run_command(f"huggingface-cli download {ASSETS['Z-Image']['repo']} {repo_path} --local-dir {LOCAL_WORKSPACE}/tmp_z")
            downloaded = glob.glob(f"{LOCAL_WORKSPACE}/tmp_z/**/{os.path.basename(repo_path)}", recursive=True)
            if downloaded:
                os.rename(downloaded[0], local_path)

    # 5. Wan 2.2 取得 (レジューム対応 wget)
    for key, (repo_path, local_path) in ASSETS["Wan2.2-I2V-14B"]["files"].items():
        if not os.path.exists(local_path):
            print(f"[*] Downloading Wan 2.2 {key}...")
            url = f"{ASSETS['Wan2.2-I2V-14B']['base_url']}/{repo_path}"
            run_command(f"wget -c {url} -O {local_path}")

    # 6. リポジトリの最新化
    run_command("git pull origin main")

    print("\n✅ 武装完了。ヘッドレス執行の準備が整いました。")

if __name__ == "__main__":
    setup_env()
