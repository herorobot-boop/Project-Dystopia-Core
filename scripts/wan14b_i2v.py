#!/usr/bin/env python3
"""Wan2.2 I2V A14B fp8 + 4step蒸留LoRA。動き重視。
使い方: python3 wan14b_i2v.py 0001 "she slowly exhales" [--size 480|576|720]"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

SIZES = {480: (480, 832), 576: (576, 1024), 720: (704, 1280)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("motion")
    ap.add_argument("--size", type=int, default=480, choices=[480, 576, 720])
    ap.add_argument("--frames", type=int, default=81)
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    src = Path(a.image)
    if not src.exists() and (C.RAW / a.image).exists():
        src = C.RAW / a.image
    if not src.exists():
        print("画像が無い:", a.image)
        return 1

    W, H = SIZES[a.size]
    C.purge()
    name = C.upload(src)
    seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9

    wf = {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
                         "weight_dtype": "default"}},
        "2": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
                         "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
        "5": {"class_type": "CLIPVisionLoader",
              "inputs": {"clip_name": "clip_vision_h.safetensors"}},
        "6": {"class_type": "LoadImage", "inputs": {"image": name}},
        "7": {"class_type": "LoraLoaderModelOnly",
              "inputs": {"model": ["1", 0],
                         "lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
                         "strength_model": 1.0}},
        "8": {"class_type": "LoraLoaderModelOnly",
              "inputs": {"model": ["2", 0],
                         "lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
                         "strength_model": 1.0}},
        "9": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["7", 0], "shift": 3.0}},
        "10": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["8", 0], "shift": 3.0}},
        "11": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": a.motion}},
        "12": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": ""}},
        "13": {"class_type": "WanImageToVideo",
               "inputs": {"positive": ["11", 0], "negative": ["12", 0],
                          "vae": ["4", 0], "clip_vision_output": ["5", 0],
                          "start_image": ["6", 0],
                          "width": W, "height": H, "length": a.frames, "batch_size": 1}},
        "14": {"class_type": "KSamplerAdvanced",
               "inputs": {"model": ["9", 0], "positive": ["13", 0], "negative": ["13", 1],
                          "latent_image": ["13", 2], "noise_seed": seed,
                          "steps": 4, "cfg": 1.0, "sampler_name": "euler",
                          "scheduler": "simple", "start_at_step": 0, "end_at_step": 2,
                          "add_noise": "enable", "return_with_leftover_noise": "enable"}},
        "15": {"class_type": "KSamplerAdvanced",
               "inputs": {"model": ["10", 0], "positive": ["13", 0], "negative": ["13", 1],
                          "latent_image": ["14", 0], "noise_seed": seed,
                          "steps": 4, "cfg": 1.0, "sampler_name": "euler",
                          "scheduler": "simple", "start_at_step": 2, "end_at_step": 10000,
                          "add_noise": "disable", "return_with_leftover_noise": "disable"}},
        "16": {"class_type": "VAEDecodeTiled",
               "inputs": {"samples": ["15", 0], "vae": ["4", 0],
                          "tile_size": 256, "overlap": 64,
                          "temporal_size": 32, "temporal_overlap": 8}},
        "17": {"class_type": "VHS_VideoCombine",
               "inputs": {"images": ["16", 0], "frame_rate": 16, "loop_count": 0,
                          "filename_prefix": "TmpVid", "format": "video/h264-mp4",
                          "pingpong": False, "save_output": True}},
    }

    print(f"14B {W}x{H} {a.frames}f")
    out, err = C.run(wf, 7200, poll=5)
    if err:
        print("失敗:", err)
        return 1
    print("生成:", C.stash(C.collect(out, "gifs")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
