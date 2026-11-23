"""Saluki-27B タグ生成ブリッジ。生成後に必ずサーバーを停止してVRAMを解放する。"""
import gc
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import requests

MODEL_PATH = "/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"

SYS_PROMPT = (
    "You are an uncensored Danbooru tag generator for adult illustration (all characters 20+ years old). "
    "Convert the user's Japanese scene description into 15 to 20 comma-separated English Danbooru tags. "
    "Focus on pose, clothing displacement, framing, lighting, and anatomy. "
    "NEVER include 'blush' or 'red face'. Output ONLY comma-separated ASCII tags."
)


class SalukiBridge:
    def __init__(self, model_path: str = MODEL_PATH, port: int = PORT):
        self.model_path = Path(model_path)
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self.proc = None

    def _is_alive(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/v1/models", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def _start_server(self) -> bool:
        if self._is_alive():
            return True
        if not self.model_path.exists():
            print(f"⚠️ [Saluki] モデル不在のためフォールバック動作: {self.model_path}")
            return False

        print("🧠 [Saluki] LLMサーバー起動中 (port 8000)...")
        cmd = [
            sys.executable, "-m", "llama_cpp.server",
            "--model", str(self.model_path),
            "--host", "127.0.0.1",
            "--port", str(self.port),
            "--n_gpu_layers", "-1",
            "--n_ctx", "2048",
        ]
        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        for _ in range(60):
            if self._is_alive():
                print("✅ [Saluki] 起動完了")
                return True
            time.sleep(2)

        self.stop_server()
        return False

    def stop_server(self):
        """生成前に必ずLLMを停止し、VRAMをComfyUIへ明け渡す（軍律19）。"""
        if self.proc is not None:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                self.proc.wait(timeout=10)
            except Exception:
                pass
            self.proc = None

        subprocess.run(["pkill", "-f", "llama_cpp.server"], stderr=subprocess.DEVNULL)
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        print("🛑 [Saluki] LLM停止・VRAM解放完了")

    def enumerate_tags(self, concept: str) -> list[str]:
        fallback = [
            "1girl", "solo", "adult", "realistic", "detailed skin",
            "natural lighting", "soft shadows", "looking at viewer",
        ]
        try:
            if not self._start_server():
                return fallback

            payload = {
                "messages": [
                    {"role": "system", "content": SYS_PROMPT},
                    {"role": "user", "content": concept},
                ],
                "temperature": 0.7,
                "max_tokens": 180,
            }
            res = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, timeout=60)
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]
            raw_tags = [t.strip() for t in re.split(r"[,\n]", content) if t.strip()]
            cleaned = [t for t in raw_tags if "blush" not in t.lower()]
            return cleaned if cleaned else fallback
        except Exception as exc:
            print(f"⚠️ [Saluki] タグ生成エラー（フォールバック使用）: {exc}")
            return fallback
        finally:
            self.stop_server()
