#!/usr/bin/env python3
"""最小のFlux 1枚で配管を確認する。成功でファイル名を返す。"""
import json
import sys
import time
from pathlib import Path
import requests

BASE = "http://127.0.0.1:8188"
OUT = Path("/workspace/ComfyUI/output")

wf = {
    "1": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"},
    },
    "2": {
        "class_type": "LoraLoader",
        "inputs": {
            "model": ["1", 0],
            "clip": ["1", 1],
            "lora_name": "aidmaNSFWunlock-FLUX-V0.2.safetensors",
            "strength_model": 0.7,
            "strength_clip": 0.7,
        },
    },
    "3": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": ["2", 1],
            "text": "aidmaNSFWunlock, japanese woman standing, black hair, knit cardigan, indoor, no blush",
        },
    },
    "4": {
        "class_type": "CLIPTextEncode",
        "inputs": {"clip": ["2", 1], "text": ""},
    },
    "5": {
        "class_type": "EmptySD3LatentImage",
        "inputs": {"width": 512, "height": 640, "batch_size": 1},
    },
    "6": {
        "class_type": "KSampler",
        "inputs": {
            "model": ["2", 0],
            "positive": ["3", 0],
            "negative": ["4", 0],
            "latent_image": ["5", 0],
            "seed": int(time.time() * 1000) % 100000000,
            "steps": 8,
            "cfg": 1.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1.0,
        },
    },
    "7": {
        "class_type": "VAEDecode",
        "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
    },
    "8": {
        "class_type": "SaveImage",
        "inputs": {"filename_prefix": "Smoke", "images": ["7", 0]},
    },
}

# 1. プロンプト投入
try:
    r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=15)
except requests.RequestException as e:
    print(f"❌ ComfyUI に接続できません: {e}")
    sys.exit(1)

if r.status_code != 200:
    print(f"❌ POST失敗 (HTTP {r.status_code}):")
    try:
        err_info = r.json()
        print(json.dumps(err_info, indent=2, ensure_ascii=False))
    except Exception:
        print(r.text[:400])
    sys.exit(1)

pid = r.json().get("prompt_id")
if not pid:
    print("❌ prompt_id が取得できませんでした")
    sys.exit(1)

# 2. 実行監視（最大180秒: 3秒 × 60回）
for _ in range(60):
    time.sleep(3)
    try:
        res = requests.get(f"{BASE}/history/{pid}", timeout=10)
        h = res.json()
    except requests.RequestException:
        continue

    if pid in h:
        item = h[pid]
        status = item.get("status", {})
        
        # エラーで停止した場合の理由取得
        if status.get("status_str") == "error":
            print(f"❌ 実行エラー: {status.get('messages', '不明なエラー')}")
            sys.exit(1)

        outs = item.get("outputs", {})
        for node in outs.values():
            if "images" in node and len(node["images"]) > 0:
                fname = node["images"][0]["filename"]
                subfolder = node["images"][0].get("subfolder", "")
                full_path = OUT / subfolder / fname if subfolder else OUT / fname
                print(f"生成: {full_path}")
                sys.exit(0)

        print("❌ 完了ステータスですが出力画像が見つかりません")
        sys.exit(1)

print("❌ タイムアウト (180秒経過)")
sys.exit(1)
