"""生成スクリプト共通。VRAM解放・LLM自動停止・out/rawへの退避。"""
import json
import shutil
import subprocess
import time
from pathlib import Path

import requests

BASE = "http://127.0.0.1:8188"
LLM = "http://127.0.0.1:8000"
ROOT = Path("/workspace/Project-Dystopia-Core")
RAW = ROOT / "out" / "raw"
COMFY_OUT = Path("/workspace/ComfyUI/output")


def ensure_dirs() -> None:
    RAW.mkdir(parents=True, exist_ok=True)


def stop_llm() -> bool:
    try:
        if requests.get(f"{LLM}/v1/models", timeout=2).status_code != 200:
            return False
    except Exception:
        return False
    subprocess.run(["pkill", "-f", "llama_cpp.server"], check=False)
    for _ in range(15):
        time.sleep(1)
        try:
            requests.get(f"{LLM}/v1/models", timeout=2)
        except Exception:
            return True
    return True


def purge(keep_llm: bool = False) -> None:
    if not keep_llm:
        stop_llm()
    try:
        requests.post(f"{BASE}/free",
                      json={"unload_models": True, "free_memory": True}, timeout=20)
        time.sleep(2)
    except Exception:
        pass


def upload(path: Path) -> str:
    with path.open("rb") as f:
        r = requests.post(f"{BASE}/upload/image",
                          files={"image": (path.name, f)}, timeout=120)
    r.raise_for_status()
    return r.json()["name"]


def run(wf: dict, timeout_s: int = 1800, poll: int = 2):
    """(outputs, error) を返す。"""
    r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=30)
    if r.status_code != 200:
        return None, f"POST {r.status_code} {r.text[:500]}"
    pid = r.json()["prompt_id"]
    for _ in range(max(1, timeout_s // poll)):
        time.sleep(poll)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
        except Exception:
            continue
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                return None, json.dumps(st, ensure_ascii=False)[:900]
            return h[pid].get("outputs", {}), None
    return None, "タイムアウト"


def _next_index() -> int:
    f = RAW / ".seq"
    n = int(f.read_text().strip() or 0) if f.exists() else 0
    n += 1
    f.write_text(str(n))
    return n


def stash(names: list[str]) -> list[str]:
    ensure_dirs()
    moved = []
    for name in names:
        src = COMFY_OUT / name
        if not src.exists():
            continue
        dst = RAW / f"{_next_index():04d}{src.suffix}"
        shutil.move(str(src), str(dst))
        moved.append(dst.name)
    return moved


def collect(outputs: dict, key: str = "images") -> list[str]:
    names = []
    for node in outputs.values():
        for name in node.get(key, []):
            names.append(name.get("filename") if isinstance(name, dict) else name)
    return [n for n in names if n]
