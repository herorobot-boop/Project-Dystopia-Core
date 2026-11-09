cat > scripts/run_qwen_image_edit.py <<'PY'
#!/usr/bin/env python3
"""Qwen-Image-Edit-2509 による自然言語ノーマスク局所露出編集。

軍律9: output/ -> input/ の同期必須。
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

DEFAULT_INSTRUCTION = "Keep everything identical. Only pull panties aside to the right, exposing her anatomy."


def edit_image_difference(base_image_name: str, edit_instruction: str, seed: int = None,
                          width: int = 896, height: int = 1152) -> str:
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()
    bridge.sync_output_to_input(base_image_name)

    if seed is None:
        seed = int(time.time() * 1000) % 1000000

    if not edit_instruction.strip().startswith("Keep everything identical"):
        edit_instruction = f"Keep everything identical. Only {edit_instruction.strip()}"

    workflow = {
        "1": {"class_type": "LoadImage", "inputs": {"image": base_image_name}},
        "2": {"class_type": "LoadDiffusionModel", "inputs": {"model_name": "qwen_image_edit_2509_fp8.safetensors"}},
        "3": {
            "class_type": "LoadCLIP",
            "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_vl"},
        },
        "4": {"class_type": "LoadVAE", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {
            "class_type": "TextEncodeQwenImageEditPlus",
            "inputs": {
                "image1": ["1", int(0)],
                "prompt": edit_instruction,
                "clip": ["3", int(0)],
                "vae": ["4", int(0)],
            },
        },
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", int(0)],
                "positive": ["5", int(0)],
                "negative": ["5", int(1)],
                "latent_image": ["6", int(0)],
                "seed": seed,
                "steps": 20,
                "cfg": 2.5,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 0.85,
            },
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", int(0)], "vae": ["4", int(0)]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "QwenEdit_Exposed", "images": ["8", int(0)]}},
    }

    print(f"✂️ [Edit] 自然言語で差分編集中: {edit_instruction}")
    edited_filename = bridge.dispatch_and_wait_media(workflow, timeout=240)
    print(f"✅ [Edit Complete] 編集完了: {edited_filename}")
    return edited_filename


def main() -> int:
    if len(sys.argv) > int(1):
        img_name = sys.argv[1]
    else:
        candidates = sorted(OUTPUT_DIR.glob("FluxedUp_Base_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            print("❌ ベース画像が見つかりません。先に run_fluxed_up_t2i.py を実行してください。")
            return 1
        img_name = candidates[int(0)].name

    instruction = sys.argv[2] if len(sys.argv) > int(2) else DEFAULT_INSTRUCTION
    seed = int(sys.argv[3]) if len(sys.argv) > int(3) else None
    edit_image_difference(img_name, instruction, seed=seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
