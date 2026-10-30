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
from scripts.audit_gate import inspect_image_locally
from scripts.c2pa_signer import sign_media_atomically

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

class MultiAgentBrainProcess(multiprocessing.Process):
    def __init__(self, user_prompt: str, queue: multiprocessing.Queue):
        super().__init__()
        self.user_prompt = user_prompt
        self.queue = queue
        self.llm_path = "/workspace/models/llm/Qwen3.5-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ4_XS.gguf"

    def run(self):
        from llama_cpp import Llama

        system_cot_prompt = (
            "あなたはProject Dystopiaの4役統合思考エンジンです。\n"
            "以下の4人の専門家として内部議論(Chain of Thought)を行い、最終的な現像・動画パラメータを出力せよ。\n\n"
            "1. 【撮影監督】: カメラアングル、被写界深度、視点移動(Pan/Tilt/Zoom)の策定。\n"
            "2. 【照明技師】: Specular反射、肌の光沢、Subsurface Scattering、陰影配置。\n"
            "3. 【衣装デザイナー】: 生地の張力、濡れ感、スパッツ・タイツの境界線密着。\n"
            "4. 【物理監査官】: SQUISH(肉体圧縮係数 0.35-0.50)、流体粘度、表面張力。\n\n"
            "【出力フォーマット】\n"
            "隠語やメタファー（バッファ、ポート等）は禁止。ストレートで高精細な英語物理描写のみで構成せよ。\n"
            "必ず以下の純粋なJSON構造のみを出力せよ。余計な解説文は禁止する。\n"
            "{\n"
            '  "cot_reasoning": "4役による議論ログ...",\n'
            '  "positive_prompt": "詳細な英語物理タグ、mature adult female、写実的な情景描写...",\n'
            '  "negative_prompt": "blurry, deformed, petite, child, teen, school_uniform...",\n'
            '  "squish_factor": 0.42,\n'
            '  "camera_motion": "Zoom In",\n'
            '  "is_distilled_model": true\n'
            "}"
        )

        print("🧠 [Brain Process] Qwen3.5 35B 子プロセス起動 (Blackwell 5090)...")
        llm = Llama(
            model_path=self.llm_path,
            n_gpu_layers=-int(1),
            n_ctx=4096,
            verbose=False
        )

        full_prompt = f"<|im_start|>system\n{system_cot_prompt}<|im_end|>\n<|im_start|>user\n{self.user_prompt}<|im_end|>\n<|im_start|>assistant\n"
        output = llm(full_prompt, max_tokens=1024, temperature=0.7)

        raw_text = safe_choices_getter(output.get("choices", []))

        del llm
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.queue.put(raw_text)
        print("🧹 [Brain Process] VRAM完全解放・子プロセス終了。")

class HK9CommandCenter:
    def __init__(self):
        self.bridge = ComfyAPIBridge()

    def run_brain_swap(self, user_input: str) -> dict:
        self.bridge.purge_comfyui_vram_cache()

        queue = multiprocessing.Queue()
        p = MultiAgentBrainProcess(user_input, queue)
        p.start()
        p.join()

        raw_result = queue.get()
        return self.bridge.extract_json_by_depth_counter(raw_result)

    def load_workflow(self, rel_path: str) -> dict:
        wf_path = WORKSPACE_DIR / rel_path
        with open(wf_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def execute_pipeline(self, free_japanese_prompt: str):
        print("\n" + "═"*60)
        print(f"🐺 [H-K9 OMEGA] 命令受領: {free_japanese_prompt}")
        print("═"*60)

        # 1. 思考フェーズ (完全自由入力 ➔ 4役CoT ➔ VRAMパージ)
        prompt_data = self.run_brain_swap(free_japanese_prompt)
        print(f"👁️ [CoT Reasoning]: {prompt_data.get('cot_reasoning', '')[:100]}...")
        print(f"✨ [Positive Prompt]: {prompt_data.get('positive_prompt', '')[:100]}...")

        # 2. 静止画現像フェーズ (Flux + Z-Image カスケード)
        still_wf = self.load_workflow("Project-Dystopia-Core/workflows/z_image_still_api.json")
        still_wf = self.bridge.inject_dynamic_parameters(still_wf, prompt_data)
        
        still_filename = self.bridge.dispatch_and_wait_media(still_wf, timeout=180)
        rendered_img_path = OUTPUT_DIR / still_filename

        # output/ から input/ への画像同期
        self.bridge.sync_output_to_input(still_filename)

        # 3. 視覚ピクセル自律検品ゲート (Qwen2.5-VL ローカル実行)
        if not inspect_image_locally(str(rendered_img_path)):
            print("❌ [AUDIT FAILED] Visual Safety Gate rejected image. Cycle aborted.")
            return

        # 4. 動画化現像フェーズ (Wan 2.2 Fun Camera)
        video_wf = self.load_workflow("Project-Dystopia-Core/workflows/wan22_fun_camera_api.json")
        video_wf = self.bridge.inject_dynamic_parameters(video_wf, prompt_data)
        video_wf = self.bridge.inject_image_to_workflow(video_wf, still_filename)

        video_filename = self.bridge.dispatch_and_wait_media(video_wf, timeout=360)
        raw_video_path = OUTPUT_DIR / video_filename

        # 5. C2PA 不可逆電子署名の付与
        sign_media_atomically(raw_video_path)

        print("\n" + "═"*60)
        print(f"🎉 [COMPLETE] 成果物が正常に出力・電子署名されました: {raw_video_path}")
        print("💡 ComfyUI画面またはJupyterLabから手元のPCへダウンロード可能です。")
        print("═"*60)

if __name__ == "__main__":
    center = HK9CommandCenter()
    test_input = "雨の夜の駅ホーム、濡れたタイツが脚に密着し光沢を放つ、カメラがローアングルからゆっくり接近"
    center.execute_pipeline(test_input)
