# =========================================================
# Project Dystopia - Phase I: Setup v7.6 [Fail-Safe Edition]
# =========================================================
import os, subprocess, shutil

COMFYUI_PATH = "/workspace/ComfyUI"

def safe_clone(url, path, alt_url=None):
    if os.path.exists(path):
        print(f"[*] Removing existing directory: {path}")
        shutil.rmtree(path)
    
    print(f"[*] Cloning: {url}")
    result = subprocess.run(f"git clone {url} {path}", shell=True)
    
    # 認証要求等で失敗した場合は代替URL(Public版)を試行
    if result.returncode != 0 and alt_url:
        print(f"[!] Primary URL failed. Switching to Public Mirror: {alt_url}")
        subprocess.run(f"git clone {alt_url} {path}", shell=True)

def setup_env():
    # 1. ComfyUI本体の完全な再構築
    safe_clone("https://github.com/comfyanonymous/ComfyUI.git", COMFYUI_PATH)
    subprocess.run(f"pip install -r {COMFYUI_PATH}/requirements.txt", shell=True)

    # 2. カスタムノードの確実な徴用 (問題の箇所を修正済)
    nodes = [
        ("https://github.com/ltdrdata/ComfyUI-Manager.git", f"{COMFYUI_PATH}/custom_nodes/ComfyUI-Manager", None),
        ("https://github.com/Kijai/ComfyUI-WanVideoWrapper.git", f"{COMFYUI_PATH}/custom_nodes/ComfyUI-WanVideoWrapper", None),
        ("https://github.com/LucianoCirino/efficiency-nodes-comfyui.git", f"{COMFYUI_PATH}/custom_nodes/efficiency-nodes-comfyui", None),
        # 認証が必要なURLを避け、最初からパブリック版(Kosinkadink)を指定
        ("https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git", f"{COMFYUI_PATH}/custom_nodes/ComfyUI-VideoHelperSuite", None)
    ]

    for url, path, alt in nodes:
        safe_clone(url, path, alt)
        if os.path.exists(f"{path}/requirements.txt"):
            subprocess.run(f"pip install -r {path}/requirements.txt", shell=True)

    print("\n✅ [H-K9] 再構築完了。次は止まりません。")

if __name__ == "__main__":
    setup_env()
