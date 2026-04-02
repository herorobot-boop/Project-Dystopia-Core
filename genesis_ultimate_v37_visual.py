import os
import subprocess
from pathlib import Path

# =========================================================
# 🏛️ Project Dystopia: Genesis V3.7 (Visual Intelligence)
# =========================================================

def run_cmd(cmd):
    print(f"🚀 [H-K9] Executing: {cmd}")
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def setup_visual_dystopia():
    print("🐺 [H-K9] 最終兵站確保：ハカセアイ式・自律型VLMパイプラインを徴用。")
    
    # 1. ディレクトリ構造の再定義
    base_path = Path("/workspace/models")
    for sub in ["vlm", "unet", "checkpoints", "loras", "clip"]:
        (base_path / sub).mkdir(parents=True, exist_ok=True)

    # 2. ハカセアイ式・中枢知能の徴用 (Qwen3.5-9B & Flux-1-Klein)
    # これにより「画像を見て正解を言語化する」機能が解放されます
    print("🧠 [Intel] Loading Qwen3.5-9B-VLM & Flux-1-Klein (High-Speed Prototype Engine)...")
    urls = {
        "vlm/qwen3.5-9b-vlm-q8.gguf": "https://huggingface.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-GGUF/resolve/main/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q8_0.gguf",
        "vlm/mmproj-qwen3.5-9b-f16.gguf": "https://huggingface.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-GGUF/resolve/main/mmproj-qwen3.5-9b-f16.gguf",
        "unet/flux-1-klein-8bit.safetensors": "https://huggingface.co/city96/Flux.1-Klein-gguf/resolve/main/flux1-klein-Q8_0.gguf"
    }
    for path, url in urls.items():
        run_cmd(f"wget -c '{url}' -O {base_path}/{path}")

    # 3. カスタムノード群の同期 (Resolution Master / GGUF Loader / VLM Prompt)
    print("🛠️ [Nodes] Syncing Ai-Hakase Specialized Nodes...")
    nodes_dir = "/workspace/ComfyUI/custom_nodes"
    repos = [
        "https://github.com/kijai/ComfyUI-llama-cpp",
        "https://github.com/city96/ComfyUI-GGUF",
        "https://github.com/ltdrdata/ComfyUI-Impact-Pack",
        "https://github.com/ZHO-ZHO-ZHO/ComfyUI-ResolutionMaster"
    ]
    for repo in repos:
        repo_name = repo.split('/')[-1]
        if not (Path(nodes_dir) / repo_name).exists():
            run_cmd(f"git clone {repo} {nodes_dir}/{repo_name}")

    # 4. 旧世代資産の抹消 (領土解放プロトコル)
    # Wan 2.1 関連の巨大なファイルを削除し、5090 の演算領域を確保
    print("🧹 [Purge] 領土解放：Wan 2.1 関連資産を抹消中...")
    run_cmd("rm -rf /workspace/models/diffusion_models/wan2.1* || true")

    print("\n✅ [H-K9] 視覚的思考回路のインストール完了。Blackwell 5090、全エンジン・イグニッション。")

if __name__ == "__main__":
    setup_visual_dystopia()
