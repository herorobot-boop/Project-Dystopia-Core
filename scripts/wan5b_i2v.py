#!/usr/bin/env python3
"""Wan2.2 TI2V-5B 微動動画。既定は素の5B 25step。--fast でTurbo下書き。"""
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
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--more-motion", action="store_true")
    ap.add_argument("--shift", type=float, default=-1.0)
    ap.add_argument("--frames", type=int, default=121)
    ap.add_argument("--size", type=int, default=720, choices=[480, 576, 720])
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

    W, H = SIZES[a.size]

    if a.fast:
        unet, steps, cfg, shift = "Wan2_2-TI2V-5B-Turbo_fp16.safetensors", 4, 1.0, 8.0
    else:
        unet, steps, cfg, shift = "wan2.2_ti2v_5B_fp16.safetensors", 25, 5.0, 8.0
    if a.more_motion:
        if a.fast:
            steps, cfg, shift = 6, 1.5, 6.0
        else:
            cfg, shift = 5.5, 5.0
    if a.shift > 0:
        shift = a.shift

    C.purge()
    name = C.upload(src)
    seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9

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
              "inputs": {"vae": ["3", 0], "width": W, "height": H,
                         "length": a.frames, "batch_size": 1, "start_image": ["4", 0]}},
        "9": {"class_type": "KSampler",
              "inputs": {"model": ["5", 0], "positive": ["6", 0], "negative": ["7", 0],
                         "latent_image": ["8", 0], "seed": seed, "steps": steps, "cfg": cfg,
                         "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "10": {"class_type": "VAEDecodeTiled",
               "inputs": {"samples": ["9", 0], "vae": ["3", 0],
                          "tile_size": 256, "overlap": 64,
                          "temporal_size": 32, "temporal_overlap": 8}},
        "11": {"class_type": "VHS_VideoCombine",
               "inputs": {"images": ["10", 0], "frame_rate": 24, "loop_count": 0,
                          "filename_prefix": "TmpVid", "format": "video/h264-mp4",
                          "pingpong": False, "save_output": True}},
    }

    print(f"unet={unet} steps={steps} cfg={cfg} shift={shift} frames={a.frames}")
    out, err = C.run(wf, 3600, poll=3)
    if err:
        print("失敗:", err)
        return 1
    print("生成:", C.stash(C.collect(out, "gifs")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
