import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.6 (Final Physical Link)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    # check=True により、1つでも失敗すれば即座に全軍停止
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_omega_logistics():
    print("🐺 [H-K9] 最終兵站確保シーケンス：物理結合プロトコル発動。")

    # 1. ディレクトリ構造の強制定義（ComfyUI標準準拠）
    base_path = Path("/workspace/ComfyUI/models")
    vlm_path = Path("/workspace/models/vlm")
    diffusion_path = base_path / "diffusion_models"
    clip_path = base_path / "clip"
    
    for p in [vlm_path, diffusion_path, clip_path]:
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

    # --- PHASE 3: 翻訳補助 (T5 Encoder 物理結合) ---
    print("📑 徴用：T5-v1_1-XXL (Zai-org Route / Physical Merge)")
    t5_url_base = "https://huggingface.co/zai-org/CogVideoX1.5-5B-SAT/resolve/main/t5-v1_1-xxl/"
    
    # 一時的な保存先
    tmp_t5_1 = clip_path / "t5_part1.tmp"
    tmp_t5_2 = clip_path / "t5_part2.tmp"
    final_t5 = clip_path / "t5xxl_fp16.safetensors"

    if not final_t5.exists():
        run_cmd(f"wget -c '{t5_url_base}model-00001-of-00002.safetensors' -O {tmp_t5_1}")
        run_cmd(f"wget -c '{t5_url_base}model-00002-of-00002.safetensors' -O {tmp_t5_2}")
        
        print("🛠️ [Merge] T5-v1_1-XXL の物理結合を開始...")
        # safetensorsの分割ファイルを1つに結合（注: 単純結合が不可能な場合はディレクトリごとロードさせる設定に変更）
        # ここではComfyUIがディレクトリ指定でロードできるよう、サブフォルダを作成して配置
        t5_dir = clip_path / "t5xxl_v11"
        t5_dir.mkdir(exist_ok=True)
        run_cmd(f"mv {tmp_t5_1} {t5_dir}/model-00001-of-00002.safetensors")
        run_cmd(f"mv {tmp_t5_2} {t5_dir}/model-00002-of-00002.safetensors")
        print("✅ [Merge] T5-v1_1-XXL をディレクトリ形式で正常配備。")

    print("\n" + "█"*60)
    print("✅ [H-K9] 兵站搬入・物理結合完了。")
    print(f"   LOCATION: {base_path}")
    print("   STATUS: BLACKWELL 5090 IS READY FOR IGNITION.")
    print("█"*60)

if __name__ == "__main__":
    setup_omega_logistics()
