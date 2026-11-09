#!/usr/bin/env python3
"""最小1枚で配管を確認。成功でファイル名を返す。"""
import json, sys, time
import requests

BASE = "http://127.0.0.1:8188"

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
    "4": {"class_type": "CLIPTextEncode",
          "inputs": {"clip": ["3", 1],
                     "text": "aidmaNSFWunlock, nsfw, japanese woman, black hair, knit cardigan, indoor, no blush"}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 1], "text": ""}},
    "6": {"class_type": "EmptySD3LatentImage",
          "inputs": {"width": 512, "height": 640, "batch_size": 1}},
    "7": {"class_type": "KSampler",
          "inputs": {"model": ["3", 0], "positive": ["4", 0], "negative": ["5", 0],
                     "latent_image": ["6", 0], "seed": 12345,
                     "steps": 8, "cfg": 1.0, "sampler_name": "euler",
                     "scheduler": "simple", "denoise": 1.0}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "Smoke", "images": ["8", 0]}},
}

r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=20)
if r.status_code != 200:
    print("POST失敗", r.status_code, r.text[:500]); sys.exit(1)
pid = r.json()["prompt_id"]

for _ in range(90):
    time.sleep(2)
    h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
    if pid in h:
        if h[pid].get("status", {}).get("status_str") == "error":
            print(json.dumps(h[pid]["status"], ensure_ascii=False)[:800]); sys.exit(1)
        for node in h[pid].get("outputs", {}).values():
            if "images" in node:
                print("生成:", node["images"][0]["filename"]); sys.exit(0)
        print("完了したが画像なし"); sys.exit(1)
print("タイムアウト"); sys.exit(1)
