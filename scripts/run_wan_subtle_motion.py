cat > scripts/run_wan_subtle_motion.py <<'PY'
#!/usr/bin/env python3
"""Wan 2.2 I2V による5秒微動動画化 + C2PA署名。

軍律7: 単一 float 制御。CFG 1.0固定 / Shift 3.0 / 81フレーム / 8ステップ。
15語制限と subtle|slow 接頭辞を自動補正する。
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

DEFAULT_MOTION = "slow rhythmic pelvic rocking, subtle breathing, chest elasticity"
NEGATIVE = "blurry, fast motion, violent movement, morphing, dissolving, deformed"


def normalize_motion(motion_prompt: str) -> str:
    clean = " ".join(motion_prompt.strip().split())
    low = clean.lower()
    if not low.startswith("subtle") and not low.startswith("slow"):
        clean = f"subtle {clean}"

    words = clean.split()
    if len(words) > int(15):
        print(f"⚠️ [Motion] {len(words)}語 -> 15語へ切り詰め")
        clean = " ".join(words[:int(15)])
    return clean


def render_subtle_motion_video(input_image_name: str, motion_prompt: str, seed: int = None,
                               width: int = 720, height: int = 1280) -> str:
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()
    bridge.sync_output_to_input(input_image_name)

    if seed is None:
        seed = int(time.time() * 1000) % 1000000

    clean_motion = normalize_motion(motion_prompt)
    width, height = align_resolution_16px(width, height)

    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": input_image_name}},
        "2": {
            "class_type": "ImageScaleToTotalPixels",
            "inputs": {"image": ["1", int(0)], "upscale_method": "bicubic", "total_pixels": 921600},
        },
        "3": {"class_type": "LoadDiffusionModel", "inputs": {"model_name": "wan2.1-t2v-14b-Q4_K_M.gguf"}},
        "4": {"class_type": "LoadCLIP", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
        "5": {"class_type": "LoadCLIPVision", "inputs": {"clip_name": "clip_vision_h.safetensors"}},
        "6": {"class_type": "LoadVAE", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "7": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["3", int(0)], "shift": 3.0}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", int(0)], "text": clean_motion}},
        "9": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", int(0)], "text": NEGATIVE}},
        "10": {
            "class_type": "WanImageToVideo",
            "inputs": {
                "positive": ["8", int(0)],
                "negative": ["9", int(0)],
                "vae": ["6", int(0)],
                "clip_vision_output": ["5", int(0)],
                "start_image": ["2", int(0)],
                "width": width,
                "height": height,
                "length": 81,
            },
        },
        "11": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["7", int(0)],
                "positive": ["10", int(0)],
                "negative": ["10", int(1)],
                "latent_image": ["10", int(2)],
                "seed": seed,
                "steps": 8,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "beta",
                "denoise": 1.0,
            },
        },
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", int(0)], "vae": ["6", int(0)]}},
        "13": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["12", int(0)],
                "frame_rate": 16,
                "format": "video/h264-mp4",
                "crf": 19,
                "filename_prefix": "Dystopia_Subtle_Wan",
            },
        },
    }

    print(f"🎬 [Wan 2.2] 微動動画レンダリング開始 (CFG 1.0 / Shift 3.0): {clean_motion}")
    video_filename = bridge.dispatch_and_wait_media(workflow, timeout=360)
    raw_video_path = OUTPUT_DIR / video_filename

    print("🔒 [C2PA] 成果物への非実在証明メタデータ注入中...")
    sign_media_atomically(raw_video_path)

    print("\n" + "═" * 60)
    print(f"🎉 【微動動画 完成】: {raw_video_path}")
    print("═" * 60 + "\n")
    return video_filename


def main() -> int:
    if len(sys.argv) > int(1):
        target_img = sys.argv[1]
    else:
        candidates = sorted(OUTPUT_DIR.glob("QwenEdit_Exposed_*.png"), key=os.path.getmtime, reverse=True)
        if not candidates:
            candidates = sorted(OUTPUT_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
        if not candidates:
            print("❌ 静止画が見つかりません。先に第2部の現像を実行してください。")
            return 1
        target_img = candidates[int(0)].name

    motion = sys.argv[2] if len(sys.argv) > int(2) else DEFAULT_MOTION
    render_subtle_motion_video(target_img, motion)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
