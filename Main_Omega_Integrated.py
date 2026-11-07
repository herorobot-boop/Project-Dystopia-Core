import os
import sys
import gc
import json
import time
import requests
import torch
import multiprocessing
from pathlib import Path

# 自律パス解決コード
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from scripts.comfy_api_bridge import ComfyAPIBridge
from scripts.audit_gate import inspect_image_locally
from scripts.c2pa_signer import sign_media_atomically
from scripts.mutation_lab import MutationLab

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass

COMFY_URL = "http://127.0.0.1:8188"
WORKSPACE_DIR = Path("/workspace")
WORKFLOW_DIR = WORKSPACE_DIR / "Project-Dystopia-Core/workflows"
OUTPUT_DIR = WORKSPACE_DIR / "ComfyUI/output"

def safe_choices_getter(choices) -> str:
    """脱・角括弧記法による choices 抽出"""
    if isinstance(choices, list) and len(choices) > int(0):
        first_choice, *_ = choices
        if isinstance(first_choice, dict):
            if "text" in first_choice:
                return str(first_choice.get("text", ""))
            elif "message" in first_choice and isinstance(first_choice["message"], dict):
                return str(first_choice["message"].get("content", ""))
        return str(first_choice)
    elif isinstance(choices, dict):
        return str(choices.get("text", ""))
    return str(choices)

class MultiAgentBrainProcess(multiprocessing.Process):
    """VRAM完全分離型 4役CoT思考＆自己添削プロセス (Underdog-Saluki-27B)"""
    def __init__(self, user_prompt: str, queue: multiprocessing.Queue, mutation_spice: str = ""):
        super().__init__()
        self.user_prompt = user_prompt
        self.queue = queue
        self.mutation_spice = mutation_spice
        self.llm_path = "/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"

    def run(self):
        from llama_cpp import Llama

        system_cot_prompt = (
            "You are the Lead Visual Director and DiT Prompt Critic for Project Dystopia.\n"
            "Analyze the user's concept across 4 roles: DoP (Camera/Angle), Gaffer (Lighting/Kelvin temps), "
            "Costume Designer (Fabric tension/Contact shadow), and Physics Auditor (Soft tissue displacement).\n\n"
            "### STRICT GOVERNANCE RULES\n"
            "1. Ban meaningless buzzwords: Strip '8k', 'masterpiece', 'physically based rendering'. Use 1/60s shutter speed.\n"
            "2. Camera grammar: Never mix Pan and Zoom in the same shot.\n"
            "3. Biomechanical compliance: squish_factor must be 0.60-0.80 with anatomical stress points.\n"
            "4. Lighting: Specify mixed Kelvin temperatures (e.g., 3200K key, 5000K ambient).\n"
            "5. NO METAPHORS: Never use code words like 'buffer' or 'port'. Output straight, authentic English descriptions only.\n\n"
            "### OUTPUT FORMAT\n"
            "Output ONLY the following JSON object:\n"
            "{\n"
            '  "cot_reasoning": "4-role internal deliberation...",\n'
            '  "positive_prompt": "medium tracking shot, [location], [lighting Kelvin], [clothing with seam stress], 1/60s shutter speed, subsurface scattering, authentic skin pores...",\n'
            '  "negative_prompt": "blurry, deformed, bad anatomy, fused fingers, asymmetric eyes, extra limbs, low resolution",\n'
            '  "squish_factor": 0.72,\n'
            '  "camera_motion": "Zoom In",\n'
            '  "video_route": "wan",\n'
            '  "is_distilled_model": true\n'
            "}"
        )

        print("\n🧠 [Brain Process] Saluki-27B MTP子プロセス起動 (Blackwell 5090)...")
        llm = Llama(
            model_path=self.llm_path,
            n_gpu_layers=-int(1),
            n_ctx=4096,
            verbose=False
        )

        augmented_input = f"{self.user_prompt}. Additional physical emphasis: {self.mutation_spice}" if self.mutation_spice else self.user_prompt
        full_prompt = f"<|im_start|>system\n{system_cot_prompt}<|im_end|>\n<|im_start|>user\n{augmented_input}<|im_end|>\n<|im_start|>assistant\n"
        output = llm(full_prompt, max_tokens=1200, temperature=0.7)

        raw_text = safe_choices_getter(output.get("choices", []))

        del llm
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.queue.put(raw_text)
        print("🧹 [Brain Process] Saluki-27B 思考完了・VRAM 100%更地化。")

class HK9CommandCenter:
    """Project Dystopia V8.4 統合司令塔"""
    def __init__(self):
        self.bridge = ComfyAPIBridge()
        self.mutation_lab = MutationLab()
        self.candidate_tags_pool = [
            "seam stress at waistband", "deep flesh indentation", "subsurface scattering",
            "cold 5000K fluorescent ambient", "warm 3200K tungsten practical key",
            "high fabric tension clinging to skin", "fluid viscosity reflection", "contact shadow"
        ]

    def run_brain_swap(self, user_input: str) -> dict:
        self.bridge.purge_comfyui_vram_cache()

        selected_spices = self.mutation_lab.select_mutated_tags(self.candidate_tags_pool, top_k=2)
        spice_text = ", ".join(selected_spices)

        queue = multiprocessing.Queue()
        p = MultiAgentBrainProcess(user_input, queue, mutation_spice=spice_text)
        p.start()
        p.join()

        raw_result = queue.get()
        parsed_data = self.bridge.extract_json_by_depth_counter(raw_result)
        parsed_data["applied_spices"] = selected_spices
        return parsed_data

    def load_workflow(self, rel_path: str) -> dict:
        wf_path = WORKSPACE_DIR / rel_path
        if not wf_path.exists():
            raise FileNotFoundError(f"ワークフロー定義が見つかりません: {wf_path}")
        with open(wf_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def execute_pipeline(self, free_japanese_prompt: str):
        print("\n" + "═"*65)
        print(f"🐺 [H-K9 OMEGA] 自律シリアルリレー点火: {free_japanese_prompt}")
        print("═"*65)

        # 1. 思考フェーズ (Saluki-27B MTP CoT思考 ➔ VRAMパージ)
        prompt_data = self.run_brain_swap(free_japanese_prompt)
        print(f"👁️ [CoT Deliberation]: {prompt_data.get('cot_reasoning', '')[:100]}...")
        print(f"✨ [Production Prompt]: {prompt_data.get('positive_prompt', '')[:100]}...")
        print(f"🎯 [Physics]: SQUISH={prompt_data.get('squish_factor')} / Camera={prompt_data.get('camera_motion')}")

        # 2. 静止画現像フェーズ (Flux + Z-Image カスケード)
        still_wf = self.load_workflow("Project-Dystopia-Core/workflows/z_image_still_api.json")
        still_wf = self.bridge.inject_dynamic_parameters(still_wf, prompt_data)
        
        print("\n🎨 [Phase 1: Still Rendering] Z-Image Turbo 2048px 受肉現像中...")
        still_filename = self.bridge.dispatch_and_wait_media(still_wf, timeout=180)
        rendered_img_path = OUTPUT_DIR / still_filename

        # output/ から input/ への画像自動同期 (LoadImage対策)
        self.bridge.sync_output_to_input(still_filename)

        # 3. 視覚ピクセル自律検品ゲート (Qwen2.5-VL ローカル実行)
        print("\n👁️ [Phase 2: Visual Audit] Qwen2.5-VL ピクセル直接視認検品中...")
        if not inspect_image_locally(str(rendered_img_path), max_retries=3):
            print("❌ [AUDIT FAILED] 視覚検品不合格。安全のためサイクルを中止します。")
            return

        # 4. 動画化現像フェーズ (Wan 2.2 または FastH3 Omni の動的ルーティング)
        chosen_route = prompt_data.get("video_route", "wan").lower()
        if chosen_route == "h3":
            video_wf = self.load_workflow("Project-Dystopia-Core/workflows/minimax_h3_audio_api.json")
            engine_label = "FastH3 Omni 8-Step (有音同期)"
        else:
            video_wf = self.load_workflow("Project-Dystopia-Core/workflows/wan22_fun_camera_api.json")
            engine_label = "Wan 2.2 Fun Camera (幾何カメラ制御)"

        video_wf = self.bridge.inject_dynamic_parameters(video_wf, prompt_data)
        video_wf = self.bridge.inject_image_to_workflow(video_wf, still_filename)

        print(f"\n🎬 [Phase 3: Video Rendering] {engine_label} による動画化現像中...")
        video_filename = self.bridge.dispatch_and_wait_media(video_wf, timeout=360)
        raw_video_path = OUTPUT_DIR / video_filename

        # 5. 法的防壁付与フェーズ (C2PA 不可逆電子署名)
        print(f"\n🔒 [Phase 4: C2PA Signing] 非実在証明メタデータ注入中: {video_filename}")
        sign_media_atomically(raw_video_path)

        # 6. 変異学習フィードバック
        applied_spices = prompt_data.get("applied_spices", [])
        if applied_spices:
            self.mutation_lab.record_feedback(applied_spices, reward=1.0)
            print("🧬 [Mutation Lab] 生成完走フィードバックを記録完了。")

        print("\n" + "═"*65)
        print(f"🎉 【完全自律サイクル完走】 成果物確定:")
        print(f"   映像ファイル: {raw_video_path}")
        print("💡 ComfyUI画面（Port 8188）またはJupyterLabから直接ダウンロードしてください。")
        print("═"*65 + "\n")

if __name__ == "__main__":
    center = HK9CommandCenter()
    
    # 複数バッチ自動周回キュー
    prompts_queue = [
        "雨の夜の駅ホーム、濡れたタイツが脚に密着し光沢を放つ、カメラがローアングルからゆっくり接近",
        "薄暗い歯科治療室、無影灯の強い白い光、リクライニングシートに横たわる女性の胸部への布地テンション"
    ]
    
    for idx, prompt_text in enumerate(prompts_queue):
        print(f"\n▶️ [Batch Job {idx + 1}/{len(prompts_queue)}] 開始")
        center.execute_pipeline(prompt_text)
