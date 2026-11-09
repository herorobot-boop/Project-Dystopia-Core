#!/usr/bin/env python3
"""最小のFlux 1枚で配管を確認する。成功でファイル名を返す。"""
import json, sys, time
from pathlib import Path
import requests

BASE = "http://127.0.0.1:8188"
OUT = Path("/workspace/ComfyUI/output")

wf = {
    "1": {"class_type": "CheckpointLoaderSimple",
          "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"}},
    "2": {"class_type": "LoraLoader",
          "inputs": {"model": ["1", 0], "clip": ["1", 1],
                     "lora_name": "aidmaNSFWunlock-FLUX-V0.2.safetensors",
                     "strength_model": 0.7, "strength_clip": 0.7}},
    "3": {"class_type": "CLIPTextEncode",
          "inputs": {"clip": ["2", 1],
                     "text": "aidmaNSFWunlock, japanese woman standing, black hair, knit cardigan, indoor, no blush"}},
    "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": ""}},
    "5": {"class_type": "EmptySD3LatentImage",
          "inputs": {"width": 512, "height": 640, "batch_size": 1}},
    "6": {"class_type": "KSampler",
          "inputs": {"model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0],
                     "latent_image": ["5", 0], "seed": int(time.time()) % 1000000,
                     "steps": 8, "cfg": 1.0, "sampler_name": "euler",
                     "scheduler": "simple", "denoise": 1.0}},
    "7": {"class_type": "VAEDecode",
          "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
    "8": {"class_type": "SaveImage",
          "inputs": {"filename_prefix": "Smoke", "images": ["7", 0]}},
}

r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=15)
if r.status_code != 200:
    print("POST失敗:", r.status_code, r.text[:400]); sys.exit(1)
pid = r.json()["prompt_id"]

for _ in range(60):
    time.sleep(2)
    h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
    if pid in h:
        outs = h[pid].get("outputs", {})
        for node in outs.values():
            if "images" in node:
                print("生成:", node["images"][0]["filename"]); sys.exit(0)
        print("完了したが画像が無い"); sys.exit(1)
print("タイムアウト"); sys.exit(1)
