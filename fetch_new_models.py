import os
import subprocess

# =========================================================
# Project Dystopia - Logistics: Model Downloader (v1.2)
# =========================================================

# 1. ターゲット資産（最新の脳と肉体）
# ※URLは実際のHF直リンクまたはトークン付きURLに書き換えてください
NEW_MODELS = {
    "Abliterated-Llama-3-GGUF": "https://huggingface.co/failspy/Llama-3-8B-Instruct-Abliterated-v3-GGUF/resolve/main/llama-3-8b-instruct-abliterated-v3.Q8_0.gguf",
    "Wan2.1-T2V-14B": "https://huggingface.co/Wan-AI/Wan2.1-T2V-14B/resolve/main/wan2.1_t2v_14b_bf16.safetensors",
    "Z-Image-Refiner-v2": "https://huggingface.co/path/to/zimage_v2.safetensors" 
}

# 2. 兵站経路の設定
LOCAL_TMP = "/workspace/tmp_models"
GDRIVE_DEST = "gdrive:/Project-Dystopia/models" # rcloneの接続名に合わせて調整

def fetch():
    print("🛰️ [H-K9 Logistics] Launching high-speed transport...")
    os.makedirs(LOCAL_TMP, exist_ok=True)

    for name, url in NEW_MODELS.items():
        print(f"\n📥 INBOUND: {name}")
        local_path = f"{LOCAL_TMP}/{name}.safetensors" if ".safetensors" not in name else f"{LOCAL_TMP}/{name}"
        
        # aria2cによる爆速ダウンロード (16セッション分割)
        res = subprocess.run([
            "aria2c", "-x", "16", "-s", "16", "-k", "1M", 
            "--console-log-level=error", "-o", os.path.basename(local_path), 
            "-d", LOCAL_TMP, url
        ])

        if res.returncode == 0:
            print(f"✅ Downloaded {name}. Moving to Gdrive...")
            # rclone copy で物理的にGdriveへ直送
            subprocess.run(["rclone", "copy", local_path, f"{GDRIVE_DEST}/Unet/"])
            os.remove(local_path) # 容量節約のため消去
            print(f"📦 {name} secured in Gdrive.")
        else:
            print(f"❌ Failed to fetch {name}. Check URL or Token.")

if __name__ == "__main__":
    # aria2cが入っていない場合の保険
    subprocess.run(["apt-get", "update", "-y"])
    subprocess.run(["apt-get", "install", "aria2", "-y"])
    fetch()
