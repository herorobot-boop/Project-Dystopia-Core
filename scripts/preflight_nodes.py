#!/usr/bin/env python3
"""実機のノード定義とファイル名を照合する。"""
import sys
from pathlib import Path
import requests

BASE = "http://127.0.0.1:8188"
CKPT_DIR = Path("/workspace/ComfyUI/models/checkpoints")
CKPTS = ("fluxed_up_13.1_fp8.safetensors",
         "fluxed_up_5.1_fp8.safetensors",
         "flux1-dev-fp8.safetensors")


def _pick_ckpt() -> str:
    for n in CKPTS:
        if (CKPT_DIR / n).exists():
            return n
    return CKPTS[-1]


NEEDED = {
    "UNETLoader": ["unet_name", "weight_dtype"],
    "CLIPLoader": ["clip_name", "type"],
    "CLIPVisionLoader": ["clip_name"],
    "VAELoader": ["vae_name"],
    "LoadImage": ["image"],
    "CheckpointLoaderSimple": ["ckpt_name"],
    "LoraLoader": ["model", "clip", "lora_name", "strength_model", "strength_clip"],
    "LoraLoaderModelOnly": ["model", "lora_name", "strength_model"],
    "CLIPTextEncode": ["clip", "text"],
    "EmptyLatentImage": ["width", "height", "batch_size"],
    "EmptySD3LatentImage": ["width", "height", "batch_size"],
    "ImageScaleToTotalPixels": ["image", "upscale_method", "total_pixels"],
    "KSampler": ["model", "positive", "negative", "latent_image", "seed", "steps",
                 "cfg", "sampler_name", "scheduler", "denoise"],
    "KSamplerAdvanced": ["model", "positive", "negative", "latent_image", "noise_seed",
                         "steps", "cfg", "sampler_name", "scheduler", "start_at_step",
                         "end_at_step", "add_noise", "return_with_leftover_noise"],
    "VAEDecode": ["samples", "vae"],
    "VAEDecodeTiled": ["samples", "vae", "tile_size", "overlap"],
    "VAEEncode": ["pixels", "vae"],
    "SaveImage": ["filename_prefix", "images"],
    "TextEncodeQwenImageEditPlus": ["clip", "prompt"],
    "Wan22ImageToVideoLatent": ["vae", "width", "height", "length", "batch_size", "start_image"],
    "WanImageToVideo": ["positive", "negative", "vae", "clip_vision_output",
                        "start_image", "width", "height", "length", "batch_size"],
    "ModelSamplingSD3": ["model", "shift"],
    "VHS_VideoCombine": ["images", "frame_rate", "filename_prefix", "format", "save_output"],
}

FILES = {
    "unet_name": ["qwen_image_edit_2509_fp8_e4m3fn.safetensors",
                  "wan2.2_ti2v_5B_fp16.safetensors"],
    "ckpt_name": [_pick_ckpt()],
    "clip_name": ["qwen_2.5_vl_7b_fp8_scaled.safetensors",
                  "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                  "clip_vision_h.safetensors"],
    "vae_name": ["qwen_image_vae.safetensors", "wan2.2_vae.safetensors"],
    "lora_name": ["aidmaNSFWunlock-FLUX-V0.2.safetensors",
                  "MS_Nude_Style_Flux_V2.safetensors",
                  "remove-clothes.safetensors"],
}

OPTIONAL_FILES = {
    "unet_name": ["qwen_image_edit_2511_fp8mixed.safetensors",
                  "qwen_image_fp8_e4m3fn.safetensors",
                  "Wan2_2-TI2V-5B-Turbo_fp16.safetensors",
                  "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
                  "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"],
    "lora_name": ["nsfw_qwen_21.safetensors",
                  "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
                  "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"],
}

bad = 0
warn = 0
try:
    info = requests.get(f"{BASE}/object_info", timeout=120).json()
except Exception as e:
    print("object_info 取得失敗:", e)
    sys.exit(1)

for cls, inputs in NEEDED.items():
    if cls not in info:
        print(f"❌ ノード無し: {cls}")
        bad += 1
        continue
    spec = info[cls].get("input", {})
    have = set(spec.get("required", {})) | set(spec.get("optional", {}))
    for name in inputs:
        if name not in have:
            print(f"❌ 入力名不一致: {cls}.{name}")
            bad += 1
    if cls == "CLIPLoader":
        types = spec.get("required", {}).get("type", [None])[0]
        for want in ("qwen_image", "wan"):
            if types and want not in types:
                print(f"❌ CLIPLoader に type={want} が無い")
                bad += 1
    if cls == "TextEncodeQwenImageEditPlus" and len(info[cls].get("output", [])) < 1:
        print("❌ TextEncodeQwenImageEditPlus の出力が無い")
        bad += 1

for field, names in FILES.items():
    for cls, inputs in NEEDED.items():
        if field not in inputs:
            continue
        opts = info.get(cls, {}).get("input", {}).get("required", {}).get(field, [[]])[0]
        if not isinstance(opts, list):
            continue
        for name in names:
            if opts and name not in opts:
                print(f"❌ ファイル未認識: {cls}.{field} に {name}")
                bad += 1

for field, names in OPTIONAL_FILES.items():
    for cls, inputs in NEEDED.items():
        if field not in inputs:
            continue
        opts = info.get(cls, {}).get("input", {}).get("required", {}).get(field, [[]])[0]
        if not isinstance(opts, list):
            continue
        for name in names:
            if opts and name not in opts:
                print(f"⚠ 任意ファイル無し: {name}")
                warn += 1

if warn:
    print(f"⚠ 任意 {warn} 件（起動は可）")

if bad:
    print(f"\n❌ 不整合 {bad} 件")
    sys.exit(1)
print("✅ 整合OK")
