import os
import sys
import gc
import json
import time
import requests
import torch
import multiprocessing
from pathlib import Path
from scripts.comfy_api_bridge import ComfyAPIBridge

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

class CriticBrainProcess(multiprocessing.Process):
    """4役CoT ＋ Venice AI風自己添削(Self-Critique)エンジン"""
    def __init__(self, user_prompt: str, queue: multiprocessing.Queue):
        super().__init__()
        self.user_prompt = user_prompt
        self.queue = queue
        self.llm_path = "/workspace/models/llm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"

    def run(self):
        from llama_cpp import Llama

        system_prompt = (
            "You are the Lead Visual Director and DiT Prompt Critic for Project Dystopia.\n"
            "Analyze the user's concept, perform a rigorous two-stage generation process, and output strict JSON.\n\n"
            "### STAGE 1: Chain of Thought (CoT) & Draft\n"
            "Formulate visual direction across 4 roles: DoP (Camera/Angle), Gaffer (Lighting/Color temp), "
            "Costume Designer (Fabric tension/Contact shadow), and Physics Auditor (Soft tissue displacement).\n\n"
            "### STAGE 2: Self-Critique (Venice AI Style Auditing)\n"
            "Critically audit your draft against these failure modes:\n"
            "1. Ban meaningless buzzwords: Strip '8k', 'masterpiece', 'physically based rendering'. Replace with 1/60s shutter speed.\n"
            "2. Camera grammar conflict: Ensure camera movement (e.g., Pan) does NOT contradict frame scale (e.g., Zoom).\n"
            "3. Biomechanical compliance: squish_factor must be 0.60-0.80 for natural human flesh. Must specify exact anatomical stress points (e.g., 'seam stress at waistband').\n"
            "4. Lighting temperature mismatch: Must specify mixed color temperatures (e.g., 3200K key fill, 5000K overhead ambient) for cinematic depth.\n\n"
            "### OUTPUT FORMAT\n"
            "Output ONLY the final JSON object:\n"
            "{\n"
            '  "self_critique": "Detailed critique of draft flaws and specific engineering adjustments made...",\n'
            '  "positive_prompt": "medium tracking shot, [location], [lighting with Kelvin temps], [clothing with seam stress], 1/60s shutter speed, subsurface scattering, authentic skin pores...",\n'
            '  "negative_prompt": "blurry, deformed, bad anatomy, fused fingers, asymmetric eyes, extra limbs, low resolution",\n'
            '  "squish_factor": 0.72,\n'
            '  "camera_motion": "Pan Right",\n'
            '  "is_distilled_model": true\n'
            "}"
        )

        print("\n🧠 [Qwen3.5] 思考 ＆ Venice AI風自己ダメ出し(Self-Critique)プロセス起動...")
        llm = Llama(
            model_path=self.llm_path,
            n_gpu_layers=-int(1),
            n_ctx=4096,
            verbose=False
        )

        full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{self.user_prompt}<|im_end|>\n<|im_start|>assistant\n"
        output = llm(full_prompt, max_tokens=1200, temperature=0.7)

        raw_text = safe_choices_getter(output.get("choices", []))

        del llm
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.queue.put(raw_text)
        print("🧹 [Qwen3.5] 思考完了・VRAM完全返還。")

def run_test_image_cycle(user_input: str):
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()

    # 1. Qwen自己ダメ出し思考
    queue = multiprocessing.Queue()
    p = CriticBrainProcess(user_input, queue)
    p.start()
    p.join()

    raw_result = queue.get()
    prompt_data = bridge.extract_json_by_depth_counter(raw_result)

    print("\n" + "═"*60)
    print("🧐 【Qwenの自律ダメ出し・批評ログ】")
    print(prompt_data.get("self_critique", ""))
    print("═"*60)
    print(f"✨ 【確定ポジティブ】: {prompt_data.get('positive_prompt', '')}")
    print(f"🎯 【生体力学SQUISH】: {prompt_data.get('squish_factor')} / 【カメラ】: {prompt_data.get('camera_motion')}")
    print("═"*60)

    # 2. 静止画受肉 (Z-Image) のみ実行
    still_wf_path = WORKFLOW_DIR / "z_image_still_api.json"
    if not still_wf_path.exists():
        print(f"❌ ワークフローファイルが見つかりません: {still_wf_path}")
        return

    with open(still_wf_path, "r", encoding="utf-8") as f:
        still_wf = json.load(f)

    still_wf = bridge.inject_dynamic_parameters(still_wf, prompt_data)
    print("\n🎨 [Rendering] Z-Image 2048px 静止画現像中...")
    still_filename = bridge.dispatch_and_wait_media(still_wf, timeout=180)

    print("\n" + "═"*60)
    print(f"🎉 【静止画現像完了】: {still_filename}")
    print("💡 スマホのブラウザ（Port 8188）で画像を確認してください。")
    print(f"👉 気に入ったら、動画化スクリプトを実行: python3 scripts/test_animate_video.py {still_filename}")
    print("═"*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > int(1):
        concept = sys.argv[int(1)]
    else:
        concept = input("💬 シチュエーションを入力してください: ")
    run_test_image_cycle(concept)
