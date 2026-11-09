#!/usr/bin/env python3
"""Wan2.2 TI2V-5B Turbo で微動動画化。704x1280 / 121frame / 24fps。
使い方: python3 wan5b_i2v.py 入力.png "she slowly exhales" [--long]"""
import argparse, json, sys, time
from pathlib import Path
import requests

BASE = "http://127.0.0.1:8188"
COMFY_OUT = Path("/workspace/ComfyUI/output")


def upload(path: Path) -> str:
    with path.open("rb") as f:
        r = requests.post(f"{BASE}/upload/image", files={"image": (path.name, f)}, timeout=60)
    r.raise_for_status()
    return r.json()["name"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("motion")
    ap.add_argument("--long", action="store_true", help="素の5B(25step/cfg5)を使う")
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    src = Path(a.image)
    if not src.exists() and (COMFY_OUT / a.image).exists():
        src = COMFY_OUT / a.image
    if not src.exists():
        print("画像が無い:", a.image); return 1

    name = upload(src)
    seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9

    unet = "wan2.2_ti2v_5B_fp16.safetensors" if a.long else "Wan2_2-TI2V-5B-Turbo_fp16.safetensors"
    steps, cfg, shift = (25, 5.0, 8.0) if a.long else (4, 1.0, 8.0)

    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": unet, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": name}},
        "5": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": shift}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": a.motion}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "8": {"class_type": "Wan22ImageToVideoLatent",
              "inputs": {"vae": ["3", 0], "width": 704, "height": 1280,
                         "length": 121, "batch_size": 1, "start_image": ["4", 0]}},
        "9": {"class_type": "KSampler",
              "inputs": {"model": ["5", 0], "positive": ["6", 0], "negative": ["7", 0],
                         "latent_image": ["8", 0], "seed": seed, "steps": steps, "cfg": cfg,
                         "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["3", 0]}},
        "11": {"class_type": "VHS_VideoCombine",
               "inputs": {"images": ["10", 0], "frame_rate": 24, "loop_count": 0,
                          "filename_prefix": f"Vid_{src.stem}", "format": "video/h264-mp4",
                          "pingpong": False, "save_output": True}},
    }

    r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=20)
    if r.status_code != 200:
        print("POST失敗", r.status_code, r.text[:600]); return 1
    pid = r.json()["prompt_id"]
    for _ in range(300):
        time.sleep(3)
        h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
        if pid in h:
            if h[pid].get("status", {}).get("status_str") == "error":
                print(json.dumps(h[pid]["status"], ensure_ascii=False)[:800]); return 1
            for node in h[pid].get("outputs", {}).values():
                for key in ("gifs", "videos"):
                    if key in node:
                        print("生成:", node[key][0]["filename"]); return 0
            print("出力なし"); return 1
    print("タイムアウト"); return 1


if __name__ == "__main__":
    raise SystemExit(main())
