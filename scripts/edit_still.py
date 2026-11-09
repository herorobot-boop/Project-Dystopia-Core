#!/usr/bin/env python3
"""Qwen-Image-Edit で差分編集。--lora で脱衣LoRA（既定強度0.55）。"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

KEEP = "Keep everything identical. "


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("instruction", nargs="?", default="")
    ap.add_argument("--lora", action="store_true")
    ap.add_argument("--lora-strength", type=float, default=0.55)
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    src = Path(a.image)
    if not src.exists() and (C.RAW / a.image).exists():
        src = C.RAW / a.image
    if not src.exists() and (C.COMFY_OUT / a.image).exists():
        src = C.COMFY_OUT / a.image
    if not src.exists():
        print("画像が無い:", a.image)
        return 1

    text = KEEP + a.instruction.strip()
    if a.lora:
        text = "remove all the clothes of the figure in the picture, " + text

    C.purge()
    name = C.upload(src)
    seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9

    wf = {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
                         "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                         "type": "qwen_image"}},
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
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "Tmp", "images": ["8", 0]}},
    }
    if a.lora:
        wf["10"] = {"class_type": "LoraLoaderModelOnly",
                    "inputs": {"model": ["1", 0],
                               "lora_name": "remove-clothes.safetensors",
                               "strength_model": a.lora_strength}}
        wf["6"]["inputs"]["model"] = ["10", 0]

    out, err = C.run(wf, 900)
    if err:
        print("失敗:", err)
        return 1
    print("生成:", C.stash(C.collect(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
