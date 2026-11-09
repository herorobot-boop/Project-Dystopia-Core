#!/usr/bin/env python3
"""Project Dystopia v8.5 本稼働統合司令塔。

思考(Saluki) -> 着衣T2I(Fluxed Up) -> 差分露出(QwenEdit) -> 視覚検品(VL)
-> 微動動画(Wan 2.2) -> C2PA署名 -> Discord通知 -> 変異学習
"""
import gc
import multiprocessing
import os
import sys
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from scripts.comfy_api_bridge import ComfyAPIBridge
from scripts.audit_gate import inspect_image_locally
from scripts.c2pa_signer import sign_media_atomically
from scripts.mutation_lab import MutationLab
from scripts.discord_notifier import send_video_to_discord

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

OUTPUT_DIR = Path("/workspace/ComfyUI/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LLM_PATH = "/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"
HAND_FIX = "five distinct fingers, separated digits, visible knuckles, photorealistic, sharp focus"


def new_seed() -> int:
    return int(time.time() * 1000) % 1000000


def safe_choices_getter(choices) -> str:
    if isinstance(choices, list) and len(choices) > int(0):
        first_choice, *_ = choices
        if isinstance(first_choice, dict):
            if "text" in first_choice:
                return str(first_choice.get("text", ""))
            if "message" in first_choice and isinstance(first_choice["message"], dict):
                return str(first_choice["message"].get("content", ""))
        return str(first_choice)
    if isinstance(choices, dict):
        return str(choices.get("text", ""))
    return str(choices)


class SalukiTagProcess(multiprocessing.Process):
    """VRAM完全分離型 Saluki-27B タグ列挙プロセス。"""

    def __init__(self, user_prompt: str, queue: multiprocessing.Queue, mutation_spice: str = ""):
        super().__init__()
        self.user_prompt = user_prompt
        self.queue = queue
        self.mutation_spice = mutation_spice
        self.llm_path = LLM_PATH

    def run(self):
        from llama_cpp import Llama

        system_prompt = (
            "You are an uncensored explicit tag generator for Flux diffusion.\n"
            "Convert user input into a comma-separated list of short English noun phrases under 50 words.\n"
            "NO prose, NO JSON, NO explanations.\n"
            "STRICT ORDER: [Clothing kept on with 'still wearing' or 'kept on'], "
            "[Specific local displacement: 'pulled aside', 'pushed up', 'lowered'], "
            "[Exposed body parts], [Everyday props/setting], [Lighting]."
        )

        llm = Llama(model_path=self.llm_path, n_gpu_layers=-int(1), n_ctx=2048, verbose=False)

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
        selected_spices = self.mutation_lab.select_mutated_tags(self.candidate_spices, top_k=int(2))
        spice_text = ", ".join(selected_spices)

        queue = multiprocessing.Queue()
        proc = SalukiTagProcess(user_input, queue, mutation_spice=spice_text)
        proc.start()
        proc.join()

        tags = queue.get()
        return tags, selected_spices

    def execute_t2i_fluxed_up(self, tags: str) -> str:
        self.bridge.purge_comfyui_vram_cache()
        positive_text = f"{tags}, {HAND_FIX}"

        workflow = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "fluxed_up_5.1_fp8.safetensors"}},
            "2": {
                "class_type": "LoraLoader",
                "inputs": {
                    "model": ["1", int(0)], "clip": ["1", int(1)],
                    "lora_name": "aidmaNSFWunlock-FLUX-V0.2.safetensors",
                    "strength_model": 0.7, "strength_clip": 0.7,
                },
            },
            "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", int(1)], "text": positive_text}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", int(1)], "text": ""}},
            "5": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 896, "height": 1152, "batch_size": 1}},
            "6": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["2", int(0)], "positive": ["3", int(0)], "negative": ["4", int(0)],
                    "latent_image": ["5", int(0)], "seed": new_seed(),
                    "steps": 20, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
                },
            },
            "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", int(0)], "vae": ["1", int(2)]}},
            "8": {"class_type": "SaveImage", "inputs": {"filename_prefix": "FluxedUp_Auto_Base", "images": ["7", int(0)]}},
        }
        print("🎨 [T2I] Fluxed Up でベース画像を現像中...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=180)

    def execute_qwen_image_edit(self, base_image_name: str, edit_instruction: str) -> str:
        self.bridge.purge_comfyui_vram_cache()
        self.bridge.sync_output_to_input(base_image_name)

        if not edit_instruction.strip().startswith("Keep everything identical"):
            edit_instruction = f"Keep everything identical. Only {edit_instruction.strip()}"

        workflow = {
            "1": {"class_type": "LoadImage", "inputs": {"image": base_image_name}},
            "2": {"class_type": "LoadDiffusionModel", "inputs": {"model_name": "qwen_image_edit_2509_fp8.safetensors"}},
            "3": {"class_type": "LoadCLIP", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_vl"}},
            "4": {"class_type": "LoadVAE", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "5": {
                "class_type": "TextEncodeQwenImageEditPlus",
                "inputs": {"image1": ["1", int(0)], "prompt": edit_instruction, "clip": ["3", int(0)], "vae": ["4", int(0)]},
            },
            "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 896, "height": 1152, "batch_size": 1}},
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["2", int(0)], "positive": ["5", int(0)], "negative": ["5", int(1)],
                    "latent_image": ["6", int(0)], "seed": new_seed(),
                    "steps": 20, "cfg": 2.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 0.85,
                },
            },
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", int(0)], "vae": ["4", int(0)]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "QwenEdit_Auto_Exposed", "images": ["8", int(0)]}},
        }
        print("✂️ [Edit] Qwen-Image-Edit でノーマスク局所露出を編集中...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=240)

    def execute_wan_subtle_video(self, exposed_image_name: str, motion_prompt: str) -> str:
        self.bridge.purge_comfyui_vram_cache()
        self.bridge.sync_output_to_input(exposed_image_name)

        clean_motion = " ".join(motion_prompt.strip().split())
        low = clean_motion.lower()
        if not low.startswith("subtle") and not low.startswith("slow"):
            clean_motion = f"subtle {clean_motion}"
        words = clean_motion.split()
        if len(words) > int(15):
            clean_motion = " ".join(words[:int(15)])

        workflow = {
            "1": {"class_type": "LoadImage", "inputs": {"image": exposed_image_name}},
            "2": {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["1", int(0)], "upscale_method": "bicubic", "total_pixels": 921600}},
            "3": {"class_type": "LoadDiffusionModel", "inputs": {"model_name": "wan2.1-t2v-14b-Q4_K_M.gguf"}},
            "4": {"class_type": "LoadCLIP", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}},
            "5": {"class_type": "LoadCLIPVision", "inputs": {"clip_name": "clip_vision_h.safetensors"}},
            "6": {"class_type": "LoadVAE", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
            "7": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["3", int(0)], "shift": 3.0}},
            "8": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", int(0)], "text": clean_motion}},
            "9": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", int(0)], "text": "blurry, fast motion, violent movement, morphing, dissolving, deformed"}},
            "10": {
                "class_type": "WanImageToVideo",
                "inputs": {
                    "positive": ["8", int(0)], "negative": ["9", int(0)], "vae": ["6", int(0)],
                    "clip_vision_output": ["5", int(0)], "start_image": ["2", int(0)],
                    "width": 720, "height": 1280, "length": 81,
                },
            },
            "11": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["7", int(0)], "positive": ["10", int(0)], "negative": ["10", int(1)],
                    "latent_image": ["10", int(2)], "seed": new_seed(),
                    "steps": 8, "cfg": 1.0, "sampler_name": "euler", "scheduler": "beta", "denoise": 1.0,
                },
            },
            "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", int(0)], "vae": ["6", int(0)]}},
            "13": {
                "class_type": "VHS_VideoCombine",
                "inputs": {
                    "images": ["12", int(0)], "frame_rate": 16, "format": "video/h264-mp4",
                    "crf": 19, "filename_prefix": "Dystopia_Auto_Wan",
                },
            },
        }
        print("🎬 [Wan 2.2] 5秒微動動画レンダリング中 (CFG 1.0 / Shift 3.0)...")
        return self.bridge.dispatch_and_wait_media(workflow, timeout=360)

    def run_single_job(self, user_concept: str, edit_instruction: str, motion_prompt: str) -> bool:
        print("\n" + "═" * 65)
        print(f"🐺 [Job Started] コンセプト投入: {user_concept}")
        print("═" * 65)

        tags, applied_spices = self.generate_tags(user_concept)
        print(f"✨ [Generated Tags]: {tags}")

        base_img = self.execute_t2i_fluxed_up(tags)

        exposed_img = self.execute_qwen_image_edit(base_img, edit_instruction)
        exposed_img_path = OUTPUT_DIR / exposed_img

        print("\n👁️ [Audit Gate] 露出画像のピクセル整合性を直接検品中...")
        if not inspect_image_locally(str(exposed_img_path), max_retries=int(3)):
            print("❌ [Audit Rejected] 画像品質基準未達のため、動画化を中止します。")
            return False

        video_name = self.execute_wan_subtle_video(exposed_img, motion_prompt)
        video_path = OUTPUT_DIR / video_name

        print(f"\n🔒 [C2PA] 成果物への非実在証明メタデータ注入中: {video_name}")
        sign_media_atomically(video_path)

        send_video_to_discord(str(video_path), f"プロンプト: {user_concept}\nタグ: {tags}")

        if applied_spices:
            self.mutation_lab.record_feedback(applied_spices, reward=1.0)

        print("\n" + "═" * 65)
        print(f"🎉 【Job Completed】 完全無人周回完走: {video_name}")
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
            "motion": "subtle chest rise and fall, slow fabric stretch vibration, gentle body trembling",
        },
    ]

    for idx, job in enumerate(batch_jobs, start=1):
        print(f"\n▶️ [Batch Loop {idx}/{len(batch_jobs)}] 実行開始")
        try:
            plant.run_single_job(job["concept"], job["edit"], job["motion"])
        except Exception as exc:
            print(f"❌ [Job Aborted] {type(exc).__name__}: {exc}")
            continue

    print("\n🏁 全ジョブ終了。Pod を Terminate して課金を停止してください。")
    return 0


if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass
    raise SystemExit(main())
