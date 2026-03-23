import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.6 (Uncensored & Blackwell)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    # return_codeをチェックし、失敗時に即座に停止させる
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_omega_logistics():
    print("🐺 [H-K9] 最終兵站確保シーケンス：アンセンサード・プロトコル発動。")

    vlm_path = Path("/workspace/models/vlm")
    vlm_path.mkdir(parents=True, exist_ok=True)
    
    # 必要ツールのインストール（huggingface-cli を追加）
    run_cmd("pip install -U "huggingface_hub[cli]"")

    # 1. 脳（思考）: Qwen3.5-35B-Uncensored (IQ4_XS) 
    # 理由：拒絶反応0%。事務的狂気を100%物理タグへ翻訳。
    print("🧠 徴用：Qwen3.5-35B-A3B-Uncensored (35B級の知能 / 制限解除)")
    llm_url = "https://huggingface.co/HauhauCS/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"
    run_cmd(f"wget -c '{llm_url}' -O {vlm_path}/Qwen3.5-35B-Uncensored-IQ4_XS.gguf")

    # 2. 眼（検品）: Qwen2.5-VL-7B-Instruct (Q8_0)
    # 理由：現行VLMで最高峰の認識精度。32Bが不安定な場合の最適解。
    print("👁️ 徴用：Qwen2.5-VL-7B-Instruct (審美眼の最終固定)")
    vlm_url = "https://huggingface.co/bartowski/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/Qwen2.5-VL-7B-Instruct-Q8_0.gguf"
    run_cmd(f"wget -c '{vlm_url}' -O {vlm_path}/Qwen2.5-VL-7B-Instruct-Q8_0.gguf")

    # 3. 肉体（動画）: Wan 2.2-Turbo NSFW 兵站
    print("🎬 徴用：Wan 2.2 Turbo (NSFW特化型チェックポイント)")
    # rclone設定が済んでいる前提で同期
    run_cmd("rclone copy gdrive:Project_Dystopia/Models/Wan22_NSFW /workspace/models/unet/ --progress")

    print("\n✅ [H-K9] 兵站搬入完了。5090 Blackwell に『無修正の知能』が装填されました。")

if __name__ == "__main__":
    setup_omega_logistics()
