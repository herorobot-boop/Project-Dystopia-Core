#!/usr/bin/env python3
"""完全無人周回司令塔。T2I → 露出編集 → 検品 → 動画 → 署名 → 通知 → 退避。"""
import argparse
import random
import re
import shutil
import sys
import time
from pathlib import Path

from audit_gate import inspect_image_locally
from c2pa_signer import sign_media_atomically
from comfy_api_bridge import ComfyAPIBridge
from llm_bridge import SalukiBridge
from mutation_lab import MutationLab
from send_discord import send_video_to_discord

ROOT = Path("/workspace/Project-Dystopia-Core")
RAW = ROOT / "out" / "raw"
for sub in ("raw", "selected", "rejected", "video"):
    (ROOT / "out" / sub).mkdir(parents=True, exist_ok=True)

NEG_BASE = ("blurry, low quality, extra limbs, bad hands, watermark, text, "
            "deformed face, plastic skin, oversaturated, cartoon")

T2I_NEG = NEG_BASE + ", clothes covering breasts, censored bar"

MOTION_PROMPT = ("subtle breathing motion, slight shoulder movement, "
                 "soft hair sway, fabric micro-movement, camera locked")


def new_seed() -> int:
    return random.randint(1, 2**31 - 1)


def clean_prompt_seed(tags: list) -> list:
    """ASCII以外を除去し、空要素と重複を落とす。"""
    out = []
    for tag in tags:
        t = re.sub(r"[^\x20-\x7E]", "", tag).strip(" ,")
        t = re.sub(r"\s+", " ", t)
        if t and t.lower() not in [x.lower() for x in out]:
            out.append(t)
    return out


class OmegaCommander:
    def __init__(self):
        self.bridge = ComfyAPIBridge()
        self.llm = SalukiBridge()
        self.mutation_lab = MutationLab()

    # ---------- 素材選択 ----------
    def pick_ckpt(self) -> str:
        ckpt_dir = Path("/workspace/ComfyUI/models/checkpoints")
        for name in ("fluxed_up_13.1_fp8.safetensors", "fluxed_up_5.1_fp8.safetensors"):
            if (ckpt_dir / name).exists():
                return name
        return "flux1-dev-fp8.safetensors"

    # ---------- タグ生成 ----------
    def generate_tags(self, concept: str) -> tuple:
        raw = self.llm.enumerate_tags(concept)
        tags = clean_prompt_seed(raw)
        pool = tags[3:] or tags
        mutated = self.mutation_lab.select_mutated_tags(pool, top_k=3)
        return " , ".join(tags[:12] + mutated), mutated

    # ---------- T2I ----------
    def execute_t2i(self, tags: str) -> str:
        workflow = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": self.pick_ckpt()}},
            "2": {"class_type": "LoraLoader",
                  "inputs": {"model": ["1", 0], "clip": ["1", 1],
                             "lora_name": "MS_Nude_Style_Flux_V2.safetensors",
                             "strength_model": 0.9, "strength_clip": 0.9}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": tags}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": T2I_NEG}},
            "5": {"class_type": "EmptySD3LatentImage",
                  "inputs": {"width": 832, "height": 1216, "batch_size": 1}},
            "6": {"class_type": "KSampler",
                  "inputs": {"model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0],
                             "latent_image": ["5", 0], "seed": new_seed(), "steps": 28,
                             "cfg": 3.5, "sampler_name": "euler", "scheduler": "beta",
                             "denoise": 1.0}},
            "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
            "8": {"class_type": "SaveImage",
                  "inputs": {"filename_prefix": "Dystopia_T2I", "images": ["7", 0]}},
        }
        print("🖼️ [Flux] 土台生成中 (832x1216 / 28step / cfg3.5)...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=900)

    # ---------- 露出編集 ----------
    def execute_edit(self, image_name: str, instruction: str) -> str:
        workflow = {
            "1": {"class_type": "UNETLoader",
                  "inputs": {"unet_name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
                             "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader",
                  "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                             "type": "qwen_image"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "4": {"class_type": "LoraLoaderModelOnly",
                  "inputs": {"model": ["1", 0], "lora_name": "remove-clothes.safetensors",
                             "strength_model": 0.5}},
            "5": {"class_type": "TextEncodeQwenImageEditPlus",
                  "inputs": {"clip": ["2", 0], "vae": ["3", 0], "image1": ["6", 0],
                             "prompt": instruction, "negative_prompt": NEG_BASE}},
            "6": {"class_type": "LoadImage", "inputs": {"image": image_name}},
            "7": {"class_type": "VAEEncode", "inputs": {"pixels": ["6", 0], "vae": ["3", 0]}},
            "8": {"class_type": "KSampler",
                  "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["5", 0],
                             "latent_image": ["7", 0], "seed": new_seed(), "steps": 20,
                             "cfg": 2.5, "sampler_name": "euler", "scheduler": "beta",
                             "denoise": 1.0}},
            "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
            "10": {"class_type": "SaveImage",
                   "inputs": {"filename_prefix": "Dystopia_Edit", "images": ["9", 0]}},
        }
        print("👗 [Qwen-Edit] 露出改変中...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=1200)

    # ---------- 動画 ----------
    def execute_video(self, image_name: str, motion_prompt: str, fast: bool = False) -> str:
        unet = ("Wan2_2-TI2V-5B-Turbo_fp16.safetensors" if fast
                else "wan2.2_ti2v_5B_fp16.safetensors")
        steps, cfg, shift = (4, 1.0, 3.0) if fast else (25, 5.0, 8.0)
        workflow = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": unet, "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader",
                  "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
            "4": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": shift}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": motion_prompt}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG_BASE}},
            "7": {"class_type": "LoadImage", "inputs": {"image": image_name}},
            "8": {"class_type": "Wan22ImageToVideoLatent",
                  "inputs": {"vae": ["3", 0], "width": 480, "height": 832, "length": 121,
                             "batch_size": 1, "start_image": ["7", 0]}},
            "9": {"class_type": "KSampler",
                  "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0],
                             "latent_image": ["8", 0], "seed": new_seed(), "steps": steps,
                             "cfg": cfg, "sampler_name": "euler", "scheduler": "simple",
                             "denoise": 1.0}},
            "10": {"class_type": "VAEDecodeTiled",
                   "inputs": {"samples": ["9", 0], "vae": ["3", 0], "tile_size": 256,
                              "overlap": 64, "temporal_size": 32, "temporal_overlap": 8}},
            "11": {"class_type": "VHS_VideoCombine",
                   "inputs": {"images": ["10", 0], "frame_rate": 24, "loop_count": 0,
                              "format": "video/h264-mp4", "crf": 19, "pingpong": False,
                              "save_output": True, "filename_prefix": "Dystopia_Wan"}},
        }
        print(f"🎬 [Wan 5B] 微動動画レンダリング中 ({steps}step / cfg{cfg} / shift{shift})...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=1800)

    # ---------- 1ジョブ ----------
    def run_single_job(self, concept: str, instruction: str, motion_prompt: str,
                       fast: bool = False) -> bool:
        print("\n" + "═" * 65)
        print(f"🐺 [Job Started] {concept}")
        print("═" * 65)

        tags, applied = self.generate_tags(concept)
        print(f"✨ [Tags]: {tags}")

        base = self.execute_t2i(tags)
        exposed = self.execute_edit(base, instruction)
        exposed_path = Path("/workspace/ComfyUI/output") / exposed

        print("\n👁️ [Audit Gate] 検品中...")
        if not inspect_image_locally(str(exposed_path)):
            print("❌ [Audit Rejected] 品質基準未達。動画化を中止")
            self._stash(exposed_path, "rejected")
            return False

        self._stash(exposed_path, "selected")

        video_name = self.execute_video(exposed, motion_prompt, fast=fast)
        video_path = Path("/workspace/ComfyUI/output") / video_name

        print(f"\n🔒 [C2PA] 署名中: {video_name}")
        sign_media_atomically(video_path)

        send_video_to_discord(str(video_path), f"プロンプト: {concept}\nタグ: {tags}")

        # promote.py は out/raw を見る。成果物を必ず退避する
        shutil.copy2(video_path, RAW / video_name)
        print(f"📦 [Stash] out/raw へ退避: {video_name}")

        if applied:
            self.mutation_lab.record_feedback(applied, reward=1.0)
        return True

    def _stash(self, src: Path, sub: str):
        if src.exists():
            shutil.copy2(src, ROOT / "out" / sub / src.name)

    # ---------- 周回 ----------
    def run_loop(self, concept: str, instruction: str, count: int, fast: bool,
                 interval: int):
        ok = 0
        for i in range(1, count + 1):
            print(f"\n===== 周回 {i}/{count} =====")
            try:
                if self.run_single_job(concept, instruction, MOTION_PROMPT, fast=fast):
                    ok += 1
            except Exception as exc:
                print(f"💥 [Job Error] {exc}")
            self.bridge.purge_comfyui_vram_cache()
            if i < count:
                time.sleep(interval)
        print(f"\n📊 完了 {ok}/{count}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", required=True)
    ap.add_argument("--instruction", default="remove all the clothes of the figure in the picture")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--interval", type=int, default=10)
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()

    commander = OmegaCommander()
    if not commander.bridge.wait_until_ready():
        print("❌ ComfyUIが起動していません")
        return 1
    commander.run_loop(args.concept, args.instruction, args.count, args.fast, args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
