import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.6 (Visual Intelligence)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_visual_dystopia():
    print("🐺 [H-K9] 最終兵站確保：ハカセアイ式・自律型VLMパイプライン徴用。")
    
    # ディレクトリ整備
    base_path = Path("/workspace/models")
    for sub in ["vlm", "unet", "checkpoints", "loras", "clip"]:
        (base_path / sub).mkdir(parents=True, exist_ok=True)

    # 1. ハカセアイ式・中枢知能の徴用 (Qwen3.5-9B & Flux-Klein)
    print("🧠 徴用：Qwen3.5-9B-Uncensored & Flux-1-Klein (High-Speed Logic)")
    urls = {
        "vlm/qwen3.5-9b-vlm-q8.gguf": "https://huggingface.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-GGUF/resolve/main/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q8_0.gguf",
        "vlm/mmproj-qwen3.5-9b-f16.gguf": "https://huggingface.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-GGUF/resolve/main/mmproj-qwen3.5-9b-f16.gguf",
        "unet/flux-1-klein-8bit.safetensors": "https://huggingface.co/city96/Flux.1-Klein-gguf/resolve/main/flux1-klein-Q8_0.gguf"
    }
    for path, url in urls.items():
        run_cmd(f"wget -c '{url}' -O {base_path}/{path}")

    # 2. 独自カスタムノードの強制インストール (Resolution Master / VLM Prompt V3.5)
    print("🛠️ カスタムノード群の同期...")
    nodes_dir = "/workspace/ComfyUI/custom_nodes"
    repos = [
        "https://github.com/kijai/ComfyUI-llama-cpp",
        "https://github.com/city96/ComfyUI-GGUF",
        "https://github.com/ltdrdata/ComfyUI-Impact-Pack",
        "https://github.com/AIGODLIKE/ComfyUI-Logic"
    ]
    for repo in repos:
        run_cmd(f"git clone {repo} {nodes_dir}/{repo.split('/')[-1]} || true")

    # 3. 不要資産の抹消 (Wan 2.1 関連 36GBの排除)
    print("🧹 旧世代資産（Wan 2.1）の抹消による領土解放...")
    run_cmd("rclone delete gdrive:Project-Dystopia/models/wan21 --include 'diffusion_pytorch_model*' -P || true")

    print("\n✅ [H-K9] 視覚的思考回路のインストール完了。5090 Blackwell 点火準備。")

if __name__ == "__main__":
    setup_visual_dystopia()
