import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.8 (Omega-Blackwell / Fixed URLs)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    # check=True により、1つでもダウンロードに失敗すれば即座に全軍停止（不完全な兵站を許さない）
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_omega_logistics():
    print("🐺 [H-K9] 最終兵站確保シーケンス：生存確定ルートへの換装および旧世代パージ開始。")

    # 1. ディレクトリ構造の再定義（ComfyUI標準 & 5090 Blackwell 最適化）
    # モデルの種類ごとに適切なフォルダへ自動配置します
    comfy_base = Path("/workspace/ComfyUI/models")
    vlm_path = Path("/workspace/models/vlm") 
    diffusion_path = comfy_base / "diffusion_models"
    unet_path = comfy_base / "unet"
    t5_path = comfy_base / "t5"
    
    for p in [vlm_path, diffusion_path, unet_path, t5_path]:
        p.mkdir(parents=True, exist_ok=True)

    # --- PHASE 1: 脳と眼 (LLM/VLM) ---
    # 思考の中枢。ハカセアイ式パイプラインの心臓部
    print("🧠 徴用：Qwen3.5-35B-Uncensored (Uncensored Brain)")
    llm_url = "https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
    run_cmd(f"wget -c '{llm_url}' -O {vlm_path}/Qwen3.5-35B-Uncensored-IQ4_XS.gguf")

    # --- PHASE 2: 高速試作機 (Flux-2-Klein 9B) ---
    # 司令官が発見した Unsloth版。8-bit版よりも「肉の物理」に強い。
    print("⚡ 徴用：Flux-2-Klein-9B (Unsloth Route - High Precision)")
    klein_url = "https://huggingface.co/unsloth/FLUX.2-klein-9B-GGUF/resolve/main/flux-2-klein-9b-Q8_0.gguf"
    run_cmd(f"wget -c '{klein_url}' -O {unet_path}/flux-2-klein-9b-Q8_0.gguf")

    # --- PHASE 3: 肉体 (Wan 2.1 / 2.2 Engine) ---
    # 主力重戦車 (14B-GGUF) と 高速機動部隊 (5B-Turbo) の二段構え
    print("🎬 徴用：Wan 2.1 T2V (City96 Route - 14B-GGUF Main Body)")
    wan_main_url = "https://huggingface.co/city96/Wan2.1-T2V-14B-gguf/resolve/main/wan2.1-t2v-14b-Q4_K_M.gguf"
    run_cmd(f"wget -c '{wan_main_url}' -O {diffusion_path}/wan2.1-t2v-14b-Q4_K_M.gguf")

    print("🏎️ 予備兵装：Wan 2.2-Turbo-5B (Kijai Route - High Speed)")
    # 15分執行（動画リレー）において無双するスピードモデル
    wan_turbo_url = "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan22-Turbo/Wan2_2-TI2V-5B-Turbo_fp16.safetensors"
    run_cmd(f"wget -c '{wan_turbo_url}' -O {diffusion_path}/wan2_2-ti2v-5b-turbo_fp16.safetensors")

    # --- PHASE 4: T5 Encoder (物理演算の翻訳補助) ---
    print("📑 徴用：T5-v1_1-XXL (Zai-org Route / Structural Optimization)")
    t5_url_base = "https://huggingface.co/zai-org/CogVideoX1.5-5B-SAT/resolve/main/t5-v1_1-xxl/"
    t5_target_dir = t5_path / "t5_v1.1_xxl"
    t5_target_dir.mkdir(exist_ok=True)
    
    # 分割ファイルのダウンロード
    run_cmd(f"wget -c '{t5_url_base}model-00001-of-00002.safetensors' -O {t5_target_dir}/model-00001-of-00002.safetensors")
    run_cmd(f"wget -c '{t5_url_base}model-00002-of-00002.safetensors' -O {t5_target_dir}/model-00002-of-00002.safetensors")

    # --- PHASE 5: 旧世代パージ (領土解放) ---
    print("🧹 [Purge] 領土解放：不要な旧世代 2.1 資産を抹消中...")
    run_cmd("rm -rf /workspace/models/diffusion_models/wan2.1* || true")
    
    print("\n" + "█"*60)
    print("✅ [H-K9] 兵站搬入完了：生存ルートへの換装を 100% 完遂。")
    print(f"   VRAM OPTIMIZED: 32GB (Blackwell 5090 Ready)")
    print(f"   PROTOTYPE: Flux-2-Klein 9B (Unsloth Precision)")
    print(f"   MAIN ENGINE: Wan 2.1 14B-GGUF (The Body)")
    print(f"   SUB ENGINE: Wan 2.2 5B-Turbo (The Speed)")
    print("█"*60)

if __name__ == "__main__":
    setup_omega_logistics()
