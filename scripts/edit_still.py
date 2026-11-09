#!/usr/bin/env python3
"""Qwen-Image-Edit で差分編集。マスクを塗らず自然言語で指示する。
使い方: python3 edit_still.py 入力.png "Only pull the bra cup down" [--lora] [--lora-strength 0.55]"""
import argparse, json, sys, time
from pathlib import Path
import requests

BASE = "http://127.0.0.1:8188"
COMFY_OUT = Path("/workspace/ComfyUI/output")

KEEP = "Keep everything identical. "


def purge() -> None:
    try:
        requests.post(f"{BASE}/free", json={"unload_models": True, "free_memory": True}, timeout=20)
        time.sleep(2)
    except Exception:
        pass


def upload(path: Path) -> str:
    with path.open("rb") as f:
        r = requests.post(f"{BASE}/upload/image", files={"image": (path.name, f)}, timeout=120)
    r.raise_for_status()
    return r.json()["name"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("instruction")
    ap.add_argument("--lora", action="store_true")
    ap.add_argument("--lora-strength", type=float, default=0.55)
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    src = Path(a.image)
    if not src.exists() and (COMFY_OUT / a.image).exists():
        src = COMFY_OUT / a.image
    if not src.exists():
        print("画像が無い:", a.image); return 1

    text = KEEP + a.instruction.strip()
    if a.lora:
        text = "remove all the clothes of the figure in the picture, " + text

    purge()
    name = upload(src)
    seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9

    wf = {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
                         "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": name}},
        "5": {"class_type": "TextEncodeQwenImageEditPlus",
              "inputs": {"clip": ["2", 0], "vae": ["3", 0], "image1": ["4", 0], "prompt": text}},
        "6": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "positive": ["5", 0], "negative": ["5", 1],
                         "latent_image": ["7", 0], "seed": seed, "steps": 20, "cfg": 2.5,
                         "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "7": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["3", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": f"Edit_{src.stem}", "images": ["8", 0]}},
    }
    if a.lora:
        wf["10"] = {"class_type": "LoraLoaderModelOnly",
                    "inputs": {"model": ["1", 0],
                               "lora_name": "remove-clothes.safetensors",
                               "strength_model": a.lora_strength}}
        wf["6"]["inputs"]["model"] = ["10", 0]

    print(f"lora={'on' if a.lora else 'off'} strength={a.lora_strength}")
    r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=30)
    if r.status_code != 200:
        print("POST失敗", r.status_code, r.text[:600]); return 1
    pid = r.json()["prompt_id"]
    for _ in range(200):
        time.sleep(2)
        h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
        if pid in h:
            if h[pid].get("status", {}).get("status_str") == "error":
                print(json.dumps(h[pid]["status"], ensure_ascii=False)[:900]); return 1
            for node in h[pid].get("outputs", {}).values():
                if "images" in node:
                    print("生成:", node["images"][0]["filename"]); return 0
            print("画像なし"); return 1
    print("タイムアウト"); return 1


if __name__ == "__main__":
    raise SystemExit(main())
