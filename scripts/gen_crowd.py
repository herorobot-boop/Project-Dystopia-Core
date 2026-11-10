#!/usr/bin/env python3
"""Qwen-Image で多人数。人数と配置を文章で指定する。
使い方: python3 gen_crowd.py "five women changing, three men filming with phones" """
import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

LORA = "nsfw_qwen_21.safetensors"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--block")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--strength", type=float, default=0.6)
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    text = a.scene
    if a.block:
        md = Path(a.block).read_text(encoding="utf-8")
        m = re.search(r"## POSITIVE[^\n]*\n+```\n(.*?)```", md, re.S)
        if m:
            text = m.group(1).strip() + ", " + text
    text += ", japanese, no blush, even skin tone"

    C.purge()

    for i in range(a.n):
        seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9 + i
        wf = {
            "1": {"class_type": "UNETLoader",
                  "inputs": {"unet_name": "qwen_image_fp8_e4m3fn.safetensors",
                             "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader",
                  "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                             "type": "qwen_image"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "4": {"class_type": "LoraLoaderModelOnly",
                  "inputs": {"model": ["1", 0], "lora_name": LORA,
                             "strength_model": a.strength}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": text}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
            "7": {"class_type": "EmptySD3LatentImage",
                  "inputs": {"width": 1216, "height": 832, "batch_size": 1}},
            "8": {"class_type": "KSampler",
                  "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0],
                             "latent_image": ["7", 0], "seed": seed, "steps": 24, "cfg": 2.8,
                             "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
            "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
            "10": {"class_type": "SaveImage",
                   "inputs": {"filename_prefix": "Tmp", "images": ["9", 0]}},
        }
        out, err = C.run(wf, 1200)
        if err:
            print("失敗:", err)
            return 1
        print("生成:", C.stash(C.collect(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
