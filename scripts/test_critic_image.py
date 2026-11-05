import os
import sys
import gc
import json
import requests
import torch
import multiprocessing
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    def __init__(self, user_prompt: str, queue: multiprocessing.Queue):
        super().__init__()
        self.user_prompt = user_prompt
        self.queue = queue
        self.llm_path = "/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"

    def run(self):
        from llama_cpp import Llama

        system_prompt = (
            "You are the Lead Visual Director and DiT Prompt Critic for Project Dystopia.\n"
            "Analyze the user's concept, perform two-stage self-critique, and output strict JSON.\n\n"
            "Directives: Ban 8k/masterpiece, eliminate camera grammar conflicts, set squish_factor to 0.60-0.80 "
            "with exact anatomical seam stress points, and specify mixed Kelvin color temperatures.\n\n"
            "Output JSON:\n"
            "{\n"
            '  "self_critique": "Critique notes...",\n'
            '  "positive_prompt": "Final prompt...",\n'
            '  "negative_prompt": "blurry, deformed, bad anatomy, fused fingers, asymmetric eyes, extra limbs, low resolution",\n'
            '  "squish_factor": 0.72,\n'
            '  "camera_motion": "Zoom In",\n'
            '  "is_distilled_model": true\n'
            "}"
        )

        print("\n🧠 [Saluki-27B] 思考 ＆ 自己ダメ出しプロセス起動...")
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

def run_test_image_cycle(user_input: str):
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()

    queue = multiprocessing.Queue()
    p = CriticBrainProcess(user_input, queue)
    p.start()
    p.join()

    raw_result = queue.get()
    prompt_data = bridge.extract_json_by_depth_counter(raw_result)

    print("\n" + "═"*60)
    print("🧐 【Salukiの自律ダメ出し・批評ログ】")
    print(prompt_data.get("self_critique", ""))
    print("═"*60)
    print(f"✨ 【確定ポジティブ】: {prompt_data.get('positive_prompt', '')}")
    print(f"🎯 【生体力学SQUISH】: {prompt_data.get('squish_factor')} / 【カメラ】: {prompt_data.get('camera_motion')}")
    print("═"*60)

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
    print("💡 スマホブラウザ（Port 8188）で画像を確認してください。")
    print(f"👉 気に入ったら、動画化スクリプトを実行: python3 scripts/test_animate_video.py {still_filename}")
    print("═"*60 + "\n")

if __name__ == "__main__":
    concept = sys.argv[int(1)] if len(sys.argv) > int(1) else input("💬 シチュエーションを入力してください: ")
    run_test_image_cycle(concept)
