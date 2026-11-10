#!/usr/bin/env python3
"""POSITIVEを読んで静止画生成。style LoRA があれば併用。"""
import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

UNLOCK = "aidmaNSFWunlock, "
STYLE = Path("/workspace/ComfyUI/models/loras/MS_Nude_Style_Flux_V2.safetensors")


def section(md: str, name: str) -> str:
    m = re.search(rf"## {name}[^\n]*\n+```\n(.*?)```", md, re.S)
    return m.group(1).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("block")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--width", type=int, default=832)
    ap.add_argument("--height", type=int, default=1216)
    ap.add_argument("--unlock", action="store_true")
    ap.add_argument("--nude", type=float, default=0.65)
    ap.add_argument("--seed", type=int, default=-1)
    a = ap.parse_args()

    md = Path(a.block).read_text(encoding="utf-8")
    pos, neg = section(md, "POSITIVE"), section(md, "NEGATIVE")
    if not pos:
        print("POSITIVE が空")
        return 1
    if a.unlock:
        pos = UNLOCK + pos

    C.purge()

    for i in range(a.n):
        seed = a.seed if a.seed >= 0 else int(time.time() * 1000) % 10**9 + i
        wf = {
            "1": {"class_type": "CheckpointLoaderSimple",
                  "inputs": {"ckpt_name": "flux1-dev-fp8.safetensors"}},
            "6": {"class_type": "EmptySD3LatentImage",
                  "inputs": {"width": a.width, "height": a.height, "batch_size": 1}},
        }
        model_src, clip_src = ["1", 0], ["1", 1]
        if STYLE.exists():
            wf["2"] = {"class_type": "LoraLoader",
                       "inputs": {"model": model_src, "clip": clip_src,
                                  "lora_name": STYLE.name,
                                  "strength_model": a.nude, "strength_clip": a.nude}}
            model_src, clip_src = ["2", 0], ["2", 1]
        if a.unlock:
            wf["3"] = {"class_type": "LoraLoader",
                       "inputs": {"model": model_src, "clip": clip_src,
                                  "lora_name": "aidmaNSFWunlock-FLUX-V0.2.safetensors",
                                  "strength_model": 0.6, "strength_clip": 0.6}}
            model_src, clip_src = ["3", 0], ["3", 1]
        wf["4"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": clip_src, "text": pos}}
        wf["5"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": clip_src, "text": neg}}
        wf["7"] = {"class_type": "KSampler",
                   "inputs": {"model": model_src, "positive": ["4", 0], "negative": ["5", 0],
                              "latent_image": ["6", 0], "seed": seed, "steps": 28,
                              "cfg": 1.0, "sampler_name": "euler",
                              "scheduler": "simple", "denoise": 1.0}}
        wf["8"] = {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}}
        wf["9"] = {"class_type": "SaveImage",
                   "inputs": {"filename_prefix": "Tmp", "images": ["8", 0]}}

        out, err = C.run(wf, 900)
        if err:
            print("失敗:", err)
            return 1
        print("生成:", C.stash(C.collect(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
