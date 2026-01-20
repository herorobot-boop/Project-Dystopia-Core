import os
import subprocess
import time
import requests
from datetime import datetime

MODEL_NAME = "chronos-hermes-13b.Q5_K_M.gguf"
MODEL_PATH = "/workspace/gdrive/MyDrive/Project-Dystopia/LLM/" + MODEL_NAME
DRAFT_MODEL_PATH = "/workspace/llm_draft/mistral-7b.Q4_K_M.gguf"
VLLM_PORT = 8000
GPU_MEMORY_UTILIZATION = 0.3
CONFIG_PATH = "/workspace/vllm_config.yaml"
LOG_PATH = "/workspace/llm_log.txt"
MAX_MODEL_LEN = 8192  # ← A100向け拡張

def build_vllm_command():
    return [
        "python3", "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL_PATH,
        "--port", str(VLLM_PORT),
        "--gpu-memory-utilization", str(GPU_MEMORY_UTILIZATION),
        "--trust-remote-code",
        "--tokenizer", MODEL_PATH,
        "--dtype", "auto",
        "--max-model-len", str(MAX_MODEL_LEN),
        "--disable-log-requests",
        "--speculative-model", DRAFT_MODEL_PATH,
        "--load-config", CONFIG_PATH
    ]

def wait_for_api(timeout=60):
    print(f"⏳ Waiting for vLLM API to become available on port {VLLM_PORT}...")
    url = f"http://localhost:{VLLM_PORT}/v1/models"
    for i in range(timeout):
        try:
            res = requests.get(url)
            if res.status_code == 200:
                print("✅ vLLM API is ready.")
                return True
        except:
            pass
        time.sleep(1)
    print("❌ Timeout: vLLM API did not become ready.")
    return False

def main():
    print("🧠 [setup_sync_llm.py] Starting Chronos-Hermes via vLLM...")
    print(f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found at {MODEL_PATH}")
        return

    if not os.path.exists(DRAFT_MODEL_PATH):
        print(f"❌ Speculative model not found at {DRAFT_MODEL_PATH}")
        return

    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Config file not found at {CONFIG_PATH}")
        return

    with open(LOG_PATH, "w") as log_file:
        process = subprocess.Popen(
            build_vllm_command(),
            stdout=log_file,
            stderr=subprocess.STDOUT
        )

    if wait_for_api():
        print("🚀 Chronos-Hermes is now serving at:")
        print(f"   http://localhost:{VLLM_PORT}/v1/chat/completions")
    else:
        print("⚠️ LLM startup failed or timed out. Check llm_log.txt for details.")

if __name__ == "__main__":
    main()
