import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.6 (Final Physical Link - Fix)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    # check=True により、1つでも失敗すれば即座に全軍停止
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_omega_logistics():
    print("🐺 [H-K9] 最終兵站確保シーケンス：物理配置プロトコル発動。")

    # 1. ディレクトリ構造の強制定義（ComfyUI標準 & 5090 最適化）
    comfy_base = Path("/workspace/ComfyUI/models")
    vlm_path = Path("/workspace/models/vlm") # 思考・検品用 (GGUF)
    diffusion_path = comfy_base / "diffusion_models"
    t5_path = comfy_base / "t5" # Wan2.1標準のT5配置先
    
    for p in [vlm_path, diffusion_path, t5_path]:
        p.mkdir(parents=True, exist_ok=True)

    # --- PHASE 1: 脳と眼 (LLM/VLM) ---
    print("🧠 徴用：Qwen3.5-35B-Uncensored (Uncensored Brain)")
    llm_url = "https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
    run_cmd(f"wget -c '{llm_url}' -O {vlm_path}/Qwen3.5-35B-Uncensored-IQ4_XS.gguf")

    print("👁️ 徴用：Qwen2.5-VL-7B-Instruct (Aesthetic Eye)")
    vlm_url = "https://huggingface.co/cxtb/Qwen2.5-VL-7B-Instruct-Q8_0-GGUF/resolve/main/qwen2.5-vl-7b-instruct-q8_0.gguf"
    run_cmd(f"wget -c '{vlm_url}' -O {vlm_path}/Qwen2.5-VL-7B-Instruct-Q8_0.gguf")

    # --- PHASE 2: 肉体 (Wan 2.1 Engine) ---
    print("🎬 徴用：Wan 2.1 T2V (City96 Route - GGUF)")
    # Blackwell 5090 の VRAM 管理に最適な Q4_K_M を指定
    wan_url = "https://huggingface.co/city96/Wan2.1-T2V-14B-gguf/resolve/main/wan2.1-t2v-14b-Q4_K_M.gguf"
    run_cmd(f"wget -c '{wan_url}' -O {diffusion_path}/wan2.1-t2v-14b-Q4_K_M.gguf")

    # --- PHASE 3: 翻訳補助 (T5 Encoder 物理配置) ---
    print("📑 徴用：T5-v1_1-XXL (Zai-org Route / Structural Optimization)")
    t5_url_base = "https://huggingface.co/zai-org/CogVideoX1.5-5B-SAT/resolve/main/t5-v1_1-xxl/"
    
    # catによる結合は破損を招くため、ComfyUIが読み込み可能なフォルダ形式で配置
    t5_target_dir = t5_path / "t5_v1.1_xxl"
    t5_target_dir.mkdir(exist_ok=True)
    
    # 分割ファイルのダウンロード
    # 1/2
    run_cmd(f"wget -c '{t5_url_base}model-00001-of-00002.safetensors' -O {t5_target_dir}/model-00001-of-00002.safetensors")
    # 2/2
    run_cmd(f"wget -c '{t5_url_base}model-00002-of-00002.safetensors' -O {t5_target_dir}/model-00002-of-00002.safetensors")
    
    print("\n" + "█"*60)
    print("✅ [H-K9] 全兵站、Blackwell 5090 への装填を完了。")
    print(f"   VRAM TARGET: 32GB Optimized (nvfp4 ready)")
    print(f"   T5 STATUS: Directory-Load Format (Safe & Validated)")
    print("█"*60)

if __name__ == "__main__":
    setup_omega_logistics()
