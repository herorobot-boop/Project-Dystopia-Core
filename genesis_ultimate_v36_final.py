import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.6 (Fixed Routes)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_omega_logistics():
    print("🐺 [H-K9] 最終兵站確保シーケンス：最新・生存ルート接続。")

    # ディレクトリ整備
    vlm_path = Path("/workspace/models/vlm")
    unet_path = Path("/workspace/models/unet")
    vlm_path.mkdir(parents=True, exist_ok=True)
    unet_path.mkdir(parents=True, exist_ok=True)

    # 1. 脳（思考）: Qwen3.5-35B-Uncensored (IQ4_XS) 
    print("🧠 徴用：Qwen3.5-35B-Uncensored")
    llm_url = "https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
    run_cmd(f"wget -c '{llm_url}' -O {vlm_path}/Qwen3.5-35B-Uncensored-IQ4_XS.gguf")

    # 2. 眼（検品）: Qwen2.5-VL-7B-Instruct (Q8_0) 
    # 司令官が発見した cxtb リポジトリ経由
    print("👁️ 徴用：Qwen2.5-VL-7B-Instruct (cxtb route)")
    vlm_url = "https://huggingface.co/cxtb/Qwen2.5-VL-7B-Instruct-Q8_0-GGUF/resolve/main/qwen2.5-vl-7b-instruct-q8_0.gguf"
    run_cmd(f"wget -c '{vlm_url}' -O {vlm_path}/Qwen2.5-VL-7B-Instruct-Q8_0.gguf")

    # 3. 肉体（動画）: Wan 2.2 Turbo
    print("🎬 徴用：Wan 2.2 Turbo (Kijai optimized)")
    wan_url = "https://huggingface.co/Kijai/WanVideo_v2.2_GGUF/resolve/main/Wan2.1-T2V-14B-GGUF-q4_k_m.safetensors"
    run_cmd(f"wget -c '{wan_url}' -O {unet_path}/wan2.2_turbo_q4.safetensors")

    print("\n✅ [H-K9] 兵站搬入完了。全てのリンクは生存、5090 への装填準備完了。")

if __name__ == "__main__":
    setup_omega_logistics()
