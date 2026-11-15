#!/usr/bin/env python3
"""Project Dystopia v8.6 本稼働統合司令塔。

思考(Saluki) -> 着衣T2I(Flux) -> 差分露出(QwenEdit) -> 視覚検品(VL)
-> 微動動画(Wan2.2 5B) -> C2PA署名 -> Discord通知 -> 変異学習
"""
import gc
import multiprocessing
import os
import queue as queue_mod
import sys
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from scripts.comfy_api_bridge import ComfyAPIBridge
from scripts.audit_gate import inspect_image_locally
from scripts.c2pa_signer import sign_media_atomically
from scripts.mutation_lab import MutationLab

try:
    from scripts.discord_notifier import send_video_to_discord
except Exception:
    def send_video_to_discord(path, text=""):
        print(f"[Discord] 通知スキップ（未導入）: {path}")


OUTPUT_DIR = Path("/workspace/ComfyUI/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LLM_PATH = "/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"
HAND_FIX = "five distinct fingers, separated digits, visible knuckles, photorealistic, sharp focus"

CKPT_DIR = Path("/workspace/ComfyUI/models/checkpoints")
CKPTS = ("fluxed_up_13.1_fp8.safetensors",
         "fluxed_up_5.1_fp8.safetensors",
         "flux1-dev-fp8.safetensors")

WAN_W, WAN_H = 480, 832
WAN_FRAMES = 81


def pick_ckpt() -> str:
    for name in CKPTS:
        if (CKPT_DIR / name).exists():
            return name
    return CKPTS[-1]


def new_seed() -> int:
    return int(time.time() * 1000) % 1000000


def safe_choices_getter(choices) -> str:
    if isinstance(choices, list) and len(choices) > 0:
        first = choices[0]
        if isinstance(first, dict):
            if "text" in first:
                return str(first.get("text", ""))
            msg = first.get("message")
            if isinstance(msg, dict):
                return str(msg.get("content", ""))
        return str(first)
    if isinstance(choices, dict):
        return str(choices.get("text", ""))
    return str(choices)


class SalukiTagProcess(multiprocessing.Process):
    """VRAM完全分離型 Saluki-27B タグ列挙プロセス。"""

    def __init__(self, user_prompt: str, q: multiprocessing.Queue, mutation_spice: str = ""):
        super().__init__()
        self.user_prompt = user_prompt
        self.queue = q
        self.mutation_spice = mutation_spice
        self.llm_path = LLM_PATH

    def run(self):
        from llama_cpp import Llama

        system_prompt = (
            "You are an uncensored explicit tag generator for Flux diffusion.\n"
            "Convert user input into a comma-separated list of short English noun phrases under 50 words.\n"
            "NO prose, NO JSON, NO explanations.\n"
            "Always end with: no blush, even skin tone.\n"
            "STRICT ORDER: [Clothing kept on with 'still wearing' or 'kept on'], "
            "[Specific local displacement: 'pulled aside', 'pushed up', 'lowered'], "
            "[Exposed body parts], [Everyday props/setting], [Lighting]."
        )

        llm = Llama(model_path=self.llm_path, n_gpu_layers=-1, n_ctx=2048, verbose=False)

        augmented = (
            f"{self.user_prompt}, {self.mutation_spice}" if self.mutation_spice else self.user_prompt
        )
        full_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{augmented}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        output = llm(full_prompt, max_tokens=150, temperature=0.3, top_p=0.9)
        raw_text = safe_choices_getter(output.get("choices", []))

        del llm
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

        self.queue.put(raw_text.strip())


class DystopiaProductionPlant:
    def __init__(self):
        self.bridge = ComfyAPIBridge()
        self.mutation_lab = MutationLab()
        self.candidate_spices = [
            "heavy skin moisture", "intense specular sheen", "seam stress at waistband",
            "subsurface scattering", "contact shadow at fabric edge", "authentic pores",
            "cold 5000K fluorescent ambient", "warm 3200K tungsten practical key",
        ]

    def generate_tags(self, user_input: str):
        self.bridge.purge_comfyui_vram_cache()
        selected = self.mutation_lab.select_mutated_tags(self.candidate_spices, top_k=2)
        spice_text = ", ".join(selected)

        q = multiprocessing.Queue()
        proc = SalukiTagProcess(user_input, q, mutation_spice=spice_text)
        proc.start()
        try:
            tags = q.get(timeout=300)
        except queue_mod.Empty:
            tags = ""
        proc.join(timeout=10)
        if proc.is_alive():
            proc.terminate()

        if not tags:
            print("⚠️ [LLM] タグ生成に失敗。コンセプトをそのまま使う")
            tags = user_input
        if "no blush" not in tags:
            tags = f"{tags}, no blush, even skin tone"
        return tags, selected

    def execute_t2i(self, tags: str) -> str:
        self.bridge.purge_comfyui_vram_cache()
        ckpt = pick_ckpt()
        positive_text = f"{tags}, {HAND_FIX}"
        print(f"   土台: {ckpt}")

        workflow = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
            "2": {
                "class_type": "LoraLoader",
                "inputs": {
                    "model": ["1", 0], "clip": ["1", 1],
                    "lora_name": "MS_Nude_Style_Flux_V2.safetensors",
                    "strength_model": 0.65, "strength_clip": 0.65,
                },
            },
            "3": {
                "class_type": "LoraLoader",
                "inputs": {
                    "model": ["2", 0], "clip": ["2", 1],
                    "lora_name": "aidmaNSFWunlock-FLUX-V0.2.safetensors",
                    "strength_model": 0.6, "strength_clip": 0.6,
                },
            },
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 1], "text": positive_text}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 1], "text": ""}},
            "6": {"class_type": "EmptySD3LatentImage",
                  "inputs": {"width": 832, "height": 1216, "batch_size": 1}},
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["3", 0], "positive": ["4", 0], "negative": ["5", 0],
                    "latent_image": ["6", 0], "seed": new_seed(),
                    "steps": 28, "cfg": 1.0, "sampler_name": "euler",
                    "scheduler": "simple", "denoise": 1.0,
                },
            },
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
            "9": {"class_type": "SaveImage",
                  "inputs": {"filename_prefix": "Auto_Base", "images": ["8", 0]}},
        }
        print("🎨 [T2I] ベース画像を現像中...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=420)

    def execute_edit(self, base_image_name: str, edit_instruction: str) -> str:
        self.bridge.purge_comfyui_vram_cache()
        self.bridge.sync_output_to_input(base_image_name)

        if not edit_instruction.strip().startswith("Keep everything identical"):
            edit_instruction = f"Keep everything identical. Only {edit_instruction.strip()}"

        src = Path("/workspace/ComfyUI/input") / base_image_name
        try:
            from PIL import Image
            with Image.open(src) as img:
                w, h = img.size
            w, h = max(256, (w // 16) * 16), max(256, (h // 16) * 16)
        except Exception:
            w, h = 832, 1216

        workflow = {
            "1": {"class_type": "UNETLoader",
                  "inputs": {"unet_name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
                             "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader",
                  "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                             "type": "qwen_image"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "4": {"class_type": "LoadImage", "inputs": {"image": base_image_name}},
            "5": {"class_type": "TextEncodeQwenImageEditPlus",
                  "inputs": {"clip": ["2", 0], "vae": ["3", 0],
                             "image1": ["4", 0], "prompt": edit_instruction}},
            "6": {"class_type": "EmptySD3LatentImage",
                  "inputs": {"width": w, "height": h, "batch_size": 1}},
            "7": {"class_type": "KSampler",
                  "inputs": {"model": ["1", 0], "positive": ["5", 0], "negative": ["5", 0],
                             "latent_image": ["6", 0], "seed": new_seed(),
                             "steps": 20, "cfg": 2.5, "sampler_name": "euler",
                             "scheduler": "simple", "denoise": 1.0}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
            "9": {"class_type": "SaveImage",
                  "inputs": {"filename_prefix": "Auto_Edit", "images": ["8", 0]}},
        }
        print("✂️ [Edit] ノーマスク局所露出を編集中...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=600)

    def execute_video(self, exposed_image_name: str, motion_prompt: str) -> str:
        self.bridge.purge_comfyui_vram_cache()
        self.bridge.sync_output_to_input(exposed_image_name)

        clean_motion = " ".join(motion_prompt.strip().split())
        low = clean_motion.lower()
        if not low.startswith("subtle") and not low.startswith("slow"):
            clean_motion = f"subtle {clean_motion}"
        words = clean_motion.split()
        if len(words) > 15:
            clean_motion = " ".join(words[:15])

        workflow = {
            "1": {"class_type": "LoadImage", "inputs": {"image": exposed_image_name}},
            "2": {"class_type": "ImageScaleToTotalPixels",
                  "inputs": {"image": ["1", 0], "upscale_method": "bicubic",
                             "total_pixels": WAN_W * WAN_H}},
            "3": {"class_type": "UNETLoader",
                  "inputs": {"unet_name": "wan2.2_ti2v_5B_fp16.safetensors",
                             "weight_dtype": "default"}},
            "4": {"class_type": "CLIPLoader",
                  "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
            "5": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
            "6": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["3", 0], "shift": 8.0}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 0], "text": clean_motion}},
            "8": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 0], "text": ""}},
            "9": {"class_type": "Wan22ImageToVideoLatent",
                  "inputs": {"vae": ["5", 0], "width": WAN_W, "height": WAN_H,
                             "length": WAN_FRAMES, "batch_size": 1, "start_image": ["2", 0]}},
            "10": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["6", 0], "positive": ["7", 0], "negative": ["8", 0],
                    "latent_image": ["9", 0], "seed": new_seed(),
                    "steps": 25, "cfg": 5.0, "sampler_name": "euler",
                    "scheduler": "simple", "denoise": 1.0,
                },
            },
            "11": {"class_type": "VAEDecodeTiled",
                   "inputs": {"samples": ["10", 0], "vae": ["5", 0],
                              "tile_size": 256, "overlap": 64,
                              "temporal_size": 32, "temporal_overlap": 8}},
            "12": {
                "class_type": "VHS_VideoCombine",
                "inputs": {
                    "images": ["11", 0], "frame_rate": 24, "loop_count": 0,
                    "format": "video/h264-mp4", "crf": 19, "pingpong": False,
                    "save_output": True, "filename_prefix": "Auto_Wan",
                },
            },
        }
        print("🎬 [Wan 2.2 5B] 微動動画レンダリング中 (25step / CFG 5.0 / shift 8.0)...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=1800)

    def run_single_job(self, user_concept: str, edit_instruction: str, motion_prompt: str) -> bool:
        print("\n" + "═" * 65)
        print(f"🐺 [Job Started] {user_concept}")
        print("═" * 65)

        tags, applied_spices = self.generate_tags(user_concept)
        print(f"✨ [Tags]: {tags}")

        base_img = self.execute_t2i(tags)
        exposed_img = self.execute_edit(base_img, edit_instruction)
        exposed_path = OUTPUT_DIR / exposed_img

        print("\n👁️ [Audit Gate] 検品中...")
        if not inspect_image_locally(str(exposed_path), max_retries=3):
            print("❌ [Audit Rejected] 品質基準未達。動画化を中止")
            return False

        video_name = self.execute_video(exposed_img, motion_prompt)
        video_path = OUTPUT_DIR / video_name

        print(f"\n🔒 [C2PA] 署名中: {video_name}")
        sign_media_atomically(video_path)

        send_video_to_discord(str(video_path), f"プロンプト: {user_concept}\nタグ: {tags}")

        if applied_spices:
            self.mutation_lab.record_feedback(applied_spices, reward=1.0)

        print("\n" + "═" * 65)
        print(f"🎉 【Job Completed】 {video_name}")
        print("═" * 65 + "\n")
        return True


def main() -> int:
    plant = DystopiaProductionPlant()

    batch_jobs = [
        {
            "concept": "雨の夜の駅ホーム、濡れたタイツが脚に密着し光沢を放つ、傘を差したまま立ち尽くす",
            "edit": "pull panties aside to the right, exposing her anatomy.",
            "motion": "slow rhythmic pelvic rocking, subtle breathing, chest elasticity",
        },
        {
            "concept": "商業施設のフィッティングルーム、買い物袋を床に置いたまま、鏡の前でカーディガンのボタンを外す",
            "edit": "pull down the left bra cup under the breast, exposing her left breast.",
            "motion": "subtle chest rise and fall, slow fabric stretch vibration",
        },
    ]

    for idx, job in enumerate(batch_jobs, start=1):
        print(f"\n▶️ [Batch {idx}/{len(batch_jobs)}]")
        try:
            plant.run_single_job(job["concept"], job["edit"], job["motion"])
        except Exception as exc:
            print(f"❌ [Aborted] {type(exc).__name__}: {exc}")
            continue

    print("\n🏁 全ジョブ終了")
    return 0


if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass
    raise SystemExit(main())
