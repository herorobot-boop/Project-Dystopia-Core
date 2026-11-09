#!/usr/bin/env python3
"""dist/blocks の .md から POSITIVE を読んで静止画を生成する。
使い方: python3 gen_still.py dist/blocks/e2/e2_menstoi_001.md --n 3"""
import argparse, json, re, sys, time
from pathlib import Path
import requests

BASE = "http://127.0.0.1:8188"
OUT = Path("/workspace/ComfyUI/output")


def section(md: str, name: str) -> str:
    m = re.search(rf"## {name}[^\n]*\n+```\n(.*?)```", md, re.S)
    return m.group(1).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("block")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--width", type=int, default=832)
    ap.add_argument("--height", type=int, default=1216)
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    md = Path(a.block).read_text(encoding="utf-8")
    pos, neg = section(md, "POSITIVE"), section(md, "NEGATIVE")
    if not pos:
        print("POSITIVE が空"); return 1

    for i in range(a.n):
        seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9 + i
        wf = {
            "1": {"class_type": "CheckpointLoaderSimple",
                  "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"}},
            "2": {"class_type": "LoraLoader",
                  "inputs": {"model": ["1", 0], "clip": ["1", 1],
                             "lora_name": "aidmaNSFWunlock-FLUX-V0.2.safetensors",
                             "strength_model": 0.7, "strength_clip": 0.7}},
            "3": {"class_type": "LoraLoader",
                  "inputs": {"model": ["2", 0], "clip": ["2", 1],
                             "lora_name": "MS_Nude_Style_Flux_V2.safetensors",
                             "strength_model": 0.8, "strength_clip": 0.8}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 1], "text": pos}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 1], "text": neg}},
            "6": {"class_type": "EmptySD3LatentImage",
                  "inputs": {"width": a.width, "height": a.height, "batch_size": 1}},
            "7": {"class_type": "KSampler",
                  "inputs": {"model": ["3", 0], "positive": ["4", 0], "negative": ["5", 0],
                             "latent_image": ["6", 0], "seed": seed, "steps": 28,
                             "cfg": 1.0, "sampler_name": "euler",
                             "scheduler": "simple", "denoise": 1.0}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
            "9": {"class_type": "SaveImage",
                  "inputs": {"filename_prefix": f"Raw_{Path(a.block).stem}", "images": ["8", 0]}},
        }
        r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=20)
        if r.status_code != 200:
            print("POST失敗", r.status_code, r.text[:400]); return 1
        pid = r.json()["prompt_id"]
        for _ in range(150):
            time.sleep(2)
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                for node in h[pid].get("outputs", {}).values():
                    if "images" in node:
                        print("生成:", node["images"][0]["filename"])
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
