#!/usr/bin/env python3
"""Fluxed Up + aidmaNSFWunlock LoRA による着衣ベースT2I現像。

軍律13: 20ステップ固定。CFG 1.0。
指の崩壊はネガティブではなくポジティブ末尾の肯定文で制御する。
"""
import sys
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.comfy_api_bridge import ComfyAPIBridge

HAND_FIX = "five distinct fingers, separated digits, visible knuckles, photorealistic, sharp focus"


def generate_base_image(prompt_tags: str, seed: int = None, width: int = 896, height: int = 1152) -> str:
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()

    if seed is None:
        seed = int(time.time() * 1000) % 1000000

    positive_text = f"aidmaNSFWunlock, {prompt_tags}, {HAND_FIX}"

    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "fluxed_up_5.1_fp8.safetensors"}},
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", int(0)],
                "clip": ["1", int(1)],
                "lora_name": "aidmaNSFWunlock-FLUX-V0.2.safetensors",
                "strength_model": 0.7,
                "strength_clip": 0.7,
            },
        },
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", int(1)], "text": positive_text}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", int(1)], "text": ""}},
        "5": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", int(0)],
                "positive": ["3", int(0)],
                "negative": ["4", int(0)],
                "latent_image": ["5", int(0)],
                "seed": seed,
                "steps": 20,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
            },
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", int(0)], "vae": ["1", int(2)]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix": "FluxedUp_Base", "images": ["7", int(0)]}},
    }

    print(f"🎨 [T2I] Fluxed Up でベース画像を現像中... (seed={seed})")
    filename = bridge.dispatch_and_wait_media(workflow, timeout=180)
    print(f"✅ [T2I Complete] 生成完了: {filename}")
    return filename


def main() -> int:
    if len(sys.argv) > int(1):
        tags = sys.argv[1]
    else:
        tags = "still wearing a beige knit sweater, open trench coat kept on, shopping bag in right hand, mall corridor"

    seed = None
    if len(sys.argv) > int(2):
        seed = int(sys.argv[2])

    generate_base_image(tags, seed=seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
