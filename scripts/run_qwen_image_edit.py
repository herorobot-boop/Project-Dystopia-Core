#!/usr/bin/env python3
"""Qwen-Image-Edit-2509 による自然言語ノーマスク局所露出編集。

定型: "Keep everything identical. Only [1点のみ]."
"""
import sys
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.comfy_api_bridge import ComfyAPIBridge

OUTPUT_DIR = Path("/workspace/ComfyUI/output")


def _pick_unet() -> str:
    d = Path("/workspace/ComfyUI/models/diffusion_models")
    for n in ("qwen_image_edit_2511_fp8mixed.safetensors",
              "qwen_image_edit_2509_fp8_e4m3fn.safetensors"):
        if (d / n).exists():
            return n
    return "qwen_image_edit_2509_fp8_e4m3fn.safetensors"


UNET = _pick_unet()

DEFAULT_INSTRUCTION = "pull panties aside to the right, exposing her anatomy"


def edit_image_difference(base_image_name: str, edit_instruction: str, seed: int = None,
                          lora: bool = False, lora_strength: float = 0.55) -> str:
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()
    bridge.sync_output_to_input(base_image_name)

    if seed is None:
        seed = int(time.time() * 1000) % 1000000

    ins = edit_instruction.strip()
    if ins.startswith("Keep everything identical"):
        ins = ins[len("Keep everything identical"):].lstrip(". ").strip()
    text = f"Keep everything identical. Only {ins}"

    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": base_image_name}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "TextEncodeQwenImageEditPlus",
              "inputs": {"image1": ["1", 0], "prompt": text, "clip": ["3", 0], "vae": ["4", 0]}},
        "6": {"class_type": "VAEEncode", "inputs": {"pixels": ["1", 0], "vae": ["4", 0]}},
        "7": {"class_type": "KSampler",
              "inputs": {"model": ["2", 0], "positive": ["5", 0], "negative": ["5", 1],
                         "latent_image": ["6", 0], "seed": seed, "steps": 20, "cfg": 2.5,
                         "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "QwenEdit_Exposed", "images": ["8", 0]}},
    }
    if lora:
        workflow["10"] = {"class_type": "LoraLoaderModelOnly",
                          "inputs": {"model": ["2", 0],
                                     "lora_name": "remove-clothes.safetensors",
                                     "strength_model": lora_strength}}
        workflow["7"]["inputs"]["model"] = ["10", 0]
        workflow["5"]["inputs"]["prompt"] = "remove all the clothes of the figure in the picture, " + text

    print(f"✂️ [Edit] 差分編集中: {text}")
    edited = bridge.dispatch_and_wait_media(workflow, timeout=300)
    print(f"✅ [Edit Complete] 編集完了: {edited}")
    return edited


def main() -> int:
    if len(sys.argv) > 1:
        img_name = sys.argv[1]
    else:
        cands = sorted(OUTPUT_DIR.glob("FluxedUp_Base_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not cands:
            print("❌ ベース画像が無い。先に run_fluxed_up_t2i.py")
            return 1
        img_name = cands[0].name

    instruction = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_INSTRUCTION
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else None
    lora = "--lora" in sys.argv
    edit_image_difference(img_name, instruction, seed=seed, lora=lora)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
