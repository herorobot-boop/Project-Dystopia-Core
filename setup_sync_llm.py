import os
import subprocess

# === 設定 ===
GDRIVE_REMOTE = "gdrive"
GDRIVE_MODEL_PATH = "AI_Models/Checkpoints/LLM"
RUNPOD_MODEL_DIR = "/workspace/llm_models"
MODEL_FILENAME = "chronos-hermes-13b-v2.Q5_K_M.gguf"
LLAMA_SERVER_URL = "https://huggingface.co/steven-tey/llama-cpp-linux-binaries/resolve/main/llama-server"
LLAMA_SERVER_PATH = "/workspace/llama-server"

def ensure_dirs():
    os.makedirs(RUNPOD_MODEL_DIR, exist_ok=True)

def sync_model():
    print("🔄 GDriveからLLMモデルを同期中...")
    result = subprocess.run([
        "rclone", "copy",
        f"{GDRIVE_REMOTE}:{GDRIVE_MODEL_PATH}",
        RUNPOD_MODEL_DIR,
        "--progress"
    ])
    if result.returncode != 0:
        print("⚠️ モデル同期に失敗しました。GDriveのパスを確認してください。")
        exit(1)
    print("✅ モデル同期完了")

def download_llama_server():
    if not os.path.exists(LLAMA_SERVER_PATH):
        print("⬇️ llama-server をダウンロード中...")
        subprocess.run([
            "wget", LLAMA_SERVER_URL,
            "-O", LLAMA_SERVER_PATH
        ], check=True)
        subprocess.run(["chmod", "+x", LLAMA_SERVER_PATH], check=True)
        print("✅ llama-server 準備完了")
    else:
        print("✅ llama-server は既に存在します")

def launch_llm():
    model_path = os.path.join(RUNPOD_MODEL_DIR, MODEL_FILENAME)
    if not os.path.exists(model_path):
        print(f"⚠️ モデルファイルが見つかりません: {model_path}")
        exit(1)

    print("🚀 LLMサーバーを起動中...")
    subprocess.Popen([
        LLAMA_SERVER_PATH,
        "--model", model_path,
        "--port", "8000",
        "--ctx-size", "4096",
        "--host", "0.0.0.0",
        "--mlock"
    ])
    print("✅ LLMサーバー起動完了（http://localhost:8000）")

if __name__ == "__main__":
    ensure_dirs()
    sync_model()
    download_llama_server()
    launch_llm()
