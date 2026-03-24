import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.6 (Final Validated Routes)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    # -c (Continue) と -O (Output) を指定し、確実に指定パスへ保存
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_omega_logistics():
    print("🐺 [H-K9] 最終兵站確保シーケンス：司令官の偵察ルートへ全軍接続。")

    # ディレクトリ整備
    vlm_path = Path("/workspace/models/vlm")
    unet_path = Path("/workspace/models/unet")
    clip_path = Path("/workspace/models/clip") # T5用
    
    for p in [vlm_path, unet_path, clip_path]:
        p.mkdir(parents=True, exist_ok=True)

    # 1. 脳（思考）: Qwen3.5-35B-Uncensored
    print("🧠 徴用：Qwen3.5-35B-Uncensored (Uncensored Brain)")
    llm_url = "https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
    run_cmd(f"wget -c '{llm_url}' -O {vlm_path}/Qwen3.5-35B-Uncensored-IQ4_XS.gguf")

    # 2. 眼（検品）: Qwen2.5-VL-7B-Instruct (Q8_0) 
    print("👁️ 徴用：Qwen2.5-VL-7B-Instruct (Aesthetic Eye)")
    vlm_url = "https://huggingface.co/cxtb/Qwen2.5-VL-7B-Instruct-Q8_0-GGUF/resolve/main/qwen2.5-vl-7b-instruct-q8_0.gguf"
    run_cmd(f"wget -c '{vlm_url}' -O {vlm_path}/Qwen2.5-VL-7B-Instruct-Q8_0.gguf")

    # 3. 肉体（動画）: Wan 2.1-T2V-14B (City96 Route)
    print("🎬 徴用：Wan 2.1 T2V (GGUF optimized)")
    wan_url = "https://huggingface.co/city96/Wan2.1-T2V-14B-gguf/resolve/main/wan2.1-t2v-14b-Q4_K_M.gguf"
    run_cmd(f"wget -c '{wan_url}' -O {unet_path}/wan2.1-t2v-14b-Q4_K_M.gguf")

    # 4. 翻訳補助（T5 Encoder）: T5-v1_1-XXL (Zai-org Route)
    print("📑 徴用：T5-v1_1-XXL (Text Encoder Parts)")
    t5_base = "https://huggingface.co/zai-org/CogVideoX1.5-5B-SAT/resolve/main/t5-v1_1-xxl/"
    for part in ["model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"]:
        run_cmd(f"wget -c '{t5_base}{part}' -O {clip_path}/{part}")

    print("\n✅ [H-K9] 兵站搬入完了。全ての防壁を突破し、5090 Blackwell は完全体となりました。")

if __name__ == "__main__":
    setup_omega_logistics()
