# =========================================================
# Project Dystopia - Model Asset Deployer (v6.2 rclone-based)
# =========================================================
import os
import subprocess
from pathlib import Path

# --- 神経接続：物理パスの定義 ---
GDRIVE_BASE = "gdrive:AI_Models"
LOCAL_MODEL_BASE = Path("/workspace/models")

def deploy_assets():
    print("🧠 [H-K9 setup_models.py] Starting specialized resource sync (rclone)...")
    
    # カテゴリとターゲットディレクトリの定義
    # Z-Image / Wan2.6 を含む「unet」を最優先
    targets = {
        "UNET (Z-Image/Wan)": "unet",
        "LoRAs (Fetish)": "loras/Fetish",
        "LoRAs (Concept)": "loras/Concept",
        "CLIP/Text Encoder": "clip",
        "VLM (Inspection)": "vlm"
    }
    
    for label, folder in targets.items():
        print(f"📦 [H-K9] Deploying {label}...")
        remote_path = f"{GDRIVE_BASE}/{folder}"
        local_path = LOCAL_MODEL_BASE / folder
        
        # rclone copy により、既存ファイルはスキップしつつ高速同期
        # --checksum を付与して破損を防ぐ
        subprocess.run([
            "rclone", "copy", remote_path, str(local_path),
            "--progress",
            "--checksum",
            "--transfers", "4",
            "--multi-thread-streams", "4"
        ])

    # 最終的な存在確認（Z-Imageが現像可能か）
    critical_files = [
        LOCAL_MODEL_BASE / "unet/zimage_6b.safetensors",
        LOCAL_MODEL_BASE / "unet/wan26_14b_fp8.safetensors"
    ]
    
    print("\n🔍 Final Integrity Check:")
    for f in critical_files:
        status = "✅ ONLINE" if f.exists() else "❌ MISSING"
        print(f"{status}: {f.name}")

if __name__ == "__main__":
    deploy_assets()
