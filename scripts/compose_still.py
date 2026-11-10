#!/usr/bin/env python3
"""2枚または3枚を1枚に合成する。image1=土台, image2=参照, image3=参照(任意)。マスク不要。
使い方: python3 compose_still.py 0001 out/ref/hand.png "his hand cups her breast" [--third out/ref/other.png]"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C


def resolve(arg: str) -> Path | None:
    for base in (Path("."), C.RAW, C.COMFY_OUT, C.ROOT):
        p = base / arg
        if p.exists():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("reference")
    ap.add_argument("instruction")
    ap.add_argument("--third", default=None)
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    b = resolve(a.base)
    r = resolve(a.reference)
    if not b or not r:
        print("画像が無い:", a.base, a.reference)
        return 1

    t = None
    if a.third:
        t = resolve(a.third)
        if not t:
            print("画像が無い:", a.third)
            return 1

    C.purge()
    n1 = C.upload(b)
    n2 = C.upload(r)
    n3 = C.upload(t) if t else None
    seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9

    text = ("Compose the two images into one. Keep the woman from image1 identical. "
            "Take only the body part from image2 and place it naturally. "
            + a.instruction.strip())

    wf = {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
                         "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                         "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": n1}},
        "5": {"class_type": "LoadImage", "inputs": {"image": n2}},
        "6": {"class_type": "TextEncodeQwenImageEditPlus",
              "inputs": {"clip": ["2", 0], "vae": ["3", 0],
                         "image1": ["4", 0], "image2": ["5", 0], "prompt": text}},
        "7": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["3", 0]}},
        "8": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "positive": ["6", 0], "negative": ["6", 1],
                         "latent_image": ["7", 0], "seed": seed, "steps": 24, "cfg": 2.5,
                         "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage",
               "inputs": {"filename_prefix": "Tmp", "images": ["9", 0]}},
    }

    if n3:
        wf["11"] = {"class_type": "LoadImage", "inputs": {"image": n3}}
        wf["6"]["inputs"]["image3"] = ["11", 0]

    out, err = C.run(wf, 900)
    if err:
        print("失敗:", err)
        return 1
    print("生成:", C.stash(C.collect(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
