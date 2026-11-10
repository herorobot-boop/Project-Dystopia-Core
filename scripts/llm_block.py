#!/usr/bin/env python3
"""日本語1行 → ローカルLLM → YAML → build。"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
SYS = ROOT / "config" / "llm_system.txt"
SCEN = ROOT / "data" / "scenarios"
LLM = "http://127.0.0.1:8000/v1/chat/completions"
GUARD = "no blush, even skin tone"
LIMIT = 880


def ensure_llm() -> bool:
    try:
        if requests.get("http://127.0.0.1:8000/v1/models", timeout=2).status_code == 200:
            return True
    except Exception:
        pass
    print("LLMを起動します（初回は数分）")
    return subprocess.run(["bash", str(ROOT / "scripts" / "llm_server.sh")]).returncode == 0


def clean(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\n", " ")
    tags = []
    for t in text.split(","):
        t = t.strip(" .。、")
        if not t or len(t) > 60:
            continue
        if not re.fullmatch(r"[A-Za-z0-9 \-_']+", t):
            continue
        tags.append(t)
    return ", ".join(dict.fromkeys(tags)[:40]) if False else ", ".join(list(dict.fromkeys(tags))[:40])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("situation")
    ap.add_argument("--engine", default="E2", choices=["E1", "E2", "E3", "E4"])
    ap.add_argument("--place", required=True)
    ap.add_argument("--title", required=True)
    a = ap.parse_args()

    if not SYS.exists():
        print("config/llm_system.txt が無い")
        return 1
    if not ensure_llm():
        print("LLM起動失敗")
        return 1

    body = {
        "messages": [
            {"role": "system", "content": SYS.read_text(encoding="utf-8")},
            {"role": "user", "content": a.situation},
        ],
        "temperature": 0.35,
        "max_tokens": 200,
    }
    try:
        r = requests.post(LLM, json=body, timeout=300)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("LLM呼び出し失敗:", e)
        return 1

    prompt = clean(raw)
    if "no blush" not in prompt:
        prompt = f"{prompt}, {GUARD}"
    prompt = prompt[:LIMIT]
    if len(prompt) < 20:
        print("短すぎる:", raw[:200])
        return 1
    print("--- タグ ---")
    print(prompt)

    subprocess.run([sys.executable, str(ROOT / "scripts" / "new_scenario.py"),
                    "--engine", a.engine, "--place", a.place, "--title", a.title],
                   check=True)
    slug = re.sub(r"[^a-z0-9]+", "_", a.place.lower()).strip("_")[:30]
    target = sorted((SCEN / f"{a.engine.lower()}_{slug}").glob("*.yaml"))[-1]

    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    data["prompt_seed"] = prompt
    data["notes"] = a.situation
    target.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                      encoding="utf-8")
    print("--- 書き込み ---")
    print(target.relative_to(ROOT))

    if subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")]).returncode != 0:
        print("⚠ 検品NG。上を直してから build すること")
        return 1
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py")], check=True)
    print(f"\n次: bash run.sh still {target.stem} --n 3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
