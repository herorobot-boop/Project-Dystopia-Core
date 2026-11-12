#!/usr/bin/env python3
"""Wan2.2 TI2V-5B による微動動画化 + C2PA署名。

15語制限と subtle|slow 接頭辞の自動補正。
"""
import os
import sys
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.comfy_api_bridge import ComfyAPIBridge, align_resolution_16px
from scripts.c2pa_signer import sign_media_atomically

OUTPUT_DIR = Path("/workspace/ComfyUI/output")
UNET = "wan2.2_ti2v_5B_fp16.safetensors"

DEFAULT_MOTION = "slow rhythmic pelvic rocking, subtle breathing, chest elasticity"
NEGATIVE = "blurry, fast motion, violent movement, morphing, dissolving, deformed"


def normalize_motion(motion_prompt: str) -> str:
    clean = " ".join(motion_prompt.strip().split())
    if not clean.lower().startswith(("subtle", "slow")):
        clean = f"subtle {clean}"
    words = clean.split()
    if len(words) > 15:
        print(f"⚠️ [Motion] {len(words)}語 -> 15語へ切り詰め")
        clean = " ".join(words[:15])
    return clean


def render_subtle_motion_video(input_image_name: str, motion_prompt: str, seed: int = None,
                               width: int = 576, height: int = 1024) -> str:
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()
    bridge.sync_output_to_input(input_image_name)

    if seed is None:
        seed = int(time.time() * 1000) % 1000000

    clean_motion = normalize_motion(motion_prompt)
    width, height = align_resolution_16px(width, height)

    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": input_image_name}},
        "2": {"class_type": "ImageScaleToTotalPixels",
              "inputs": {"image": ["1", 0], "upscale_method": "bicubic", "total_pixels": 589824}},
        "3": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "4": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
        "6": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["3", 0], "shift": 3.0}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 0], "text": clean_motion}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 0], "text": NEGATIVE}},
        "9": {"class_type": "Wan22ImageToVideoLatent",
              "inputs": {"vae": ["5", 0], "width": width, "height": height,
                         "length": 81, "batch_size": 1, "start_image": ["2", 0]}},
        "10": {"class_type": "KSampler",
               "inputs": {"model": ["6", 0], "positive": ["7", 0], "negative": ["8", 0],
                          "latent_image": ["9", 0], "seed": seed, "steps": 20, "cfg": 3.0,
                          "sampler_name": "euler", "scheduler": "beta", "denoise": 1.0}},
        "11": {"class_type": "VAEDecodeTiled",
               "inputs": {"samples": ["10", 0], "vae": ["5", 0],
                          "tile_size": 256, "overlap": 64,
                          "temporal_size": 32, "temporal_overlap": 8}},
        "12": {"class_type": "VHS_VideoCombine",
               "inputs": {"images": ["11", 0], "frame_rate": 16,
                          "format": "video/h264-mp4", "crf": 19,
                          "filename_prefix": "Dystopia_Subtle_Wan"}},
    }

    print(f"🎬 [Wan 5B] 微動動画レンダリング (CFG 3.0 / Shift 3.0 / {width}x{height}): {clean_motion}")
    video_filename = bridge.dispatch_and_wait_media(workflow, timeout=1800)
    raw_video_path = OUTPUT_DIR / video_filename

    print("🔒 [C2PA] メタデータ注入中...")
    sign_media_atomically(raw_video_path)

    print(f"\n🎉 完成: {raw_video_path}\n")
    return video_filename


def main() -> int:
    if len(sys.argv) > 1:
        target_img = sys.argv[1]
    else:
        cands = sorted(OUTPUT_DIR.glob("QwenEdit_Exposed_*.png"), key=os.path.getmtime, reverse=True)
        if not cands:
            cands = sorted(OUTPUT_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
        if not cands:
            print("❌ 静止画が無い。先に現像を。")
            return 1
        target_img = cands[0].name

    motion = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MOTION
    render_subtle_motion_video(target_img, motion)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
