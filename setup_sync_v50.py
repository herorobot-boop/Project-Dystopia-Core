import os
import subprocess
import shutil

G_ROOT = "gdrive:AI_Models"
VERSION = "v50"

def run_command(command, message):
    print(f"\n➤ [{message}]...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ OK")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ {message} でエラーが発生しました: {e}")

def main():
    print(f"\n=== 🌌 Project Dystopia: Setup {VERSION} ===\n")
    
    # 1. システムツール
    run_command("apt-get update && apt-get install -y aria2 git wget unzip libgl1-mesa-glx libglib2.0-0", "System Tools")

    # 2. ComfyUI本体
    if not os.path.exists("ComfyUI"):
        run_command("git clone https://github.com/comfyanonymous/ComfyUI.git", "ComfyUI Clone")
    
    run_command("pip install --upgrade pip", "Update Pip")
    run_command("pip install -r ComfyUI/requirements.txt", "Base Requirements")

    # 3. カスタムノード
    nodes = {
        "ComfyUI-Manager": "https://github.com/ltdrdata/ComfyUI-Manager.git",
        "ComfyUI-Impact-Pack": "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git",
        "ComfyUI-Essentials": "https://github.com/cubiq/ComfyUI_essentials.git",
        "ControlNet-Auxiliary-Preprocessors": "https://github.com/Fannovel16/comfyui_controlnet_aux.git"
    }
    for name, url in nodes.items():
        path = f"ComfyUI/custom_nodes/{name}"
        if not os.path.exists(path):
            run_command(f"git clone {url} {path}", f"Clone {name}")

    run_command("pip install --upgrade ultralytics segment-anything color-matcher gradio", "Extra Libs")

    # 4. GDrive同期
    sync_paths = [("checkpoints", "checkpoints"), ("loras", "loras"), ("controlnet", "controlnet")]
    for g, l in sync_paths:
        local_dir = f"ComfyUI/models/{l}"
        os.makedirs(local_dir, exist_ok=True)
        run_command(f"rclone sync {G_ROOT}/{g} {local_dir} --progress", f"Sync {g}")

    print(f"\n✅ Setup Complete.")

if __name__ == "__main__":
    main()