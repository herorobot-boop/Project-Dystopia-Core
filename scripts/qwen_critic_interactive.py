import os
import sys
import gc
import json
import torch
import multiprocessing
from pathlib import Path
from scripts.comfy_api_bridge import ComfyAPIBridge

# CUDA Start Method ＆ VRAMアロケータ最適化
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass

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

class InteractiveCriticProcess(multiprocessing.Process):
    """4役CoT思考 ＋ Venice AI風自己添削(Self-Critique)子プロセス"""
    def __init__(self, user_prompt: str, queue: multiprocessing.Queue):
        super().__init__()
        self.user_prompt = user_prompt
        self.queue = queue
        self.llm_path = "/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"

    def run(self):
        from llama_cpp import Llama

        system_prompt = (
            "You are the Lead Visual Director and DiT Prompt Critic for Project Dystopia.\n"
            "Analyze the user's concept and output a strict JSON object containing your raw draft, "
            "a rigorous Venice-AI-style self-critique, and the finalized production prompt.\n\n"
            "### AUDITING DIRECTIVES (Venice AI Style)\n"
            "1. Ban meaningless buzzwords: Strip '8k', 'masterpiece', 'physically based rendering'. "
            "Replace with 1/60s shutter speed and optical properties.\n"
            "2. Resolve shot conflicts: Ensure camera tracking and lens focal length are strictly harmonious. "
            "Never mix Pan and Zoom in the same shot.\n"
            "3. Biomechanical compliance: squish_factor must be 0.60-0.80 for natural human flesh. "
            "Must specify exact anatomical stress points (e.g., 'seam stress at waistband', 'flesh indentation').\n"
            "4. Lighting temperature mismatch: Specify mixed Kelvin temperatures (e.g., 3200K tungsten key, 5000K ambient fluorescent).\n\n"
            "### JSON OUTPUT SCHEMA\n"
            "{\n"
            '  "raw_draft_positive": "Initial draft prompt before critique...",\n'
            '  "self_critique": "Venice AI style sharp critique detailing specific flaws in the draft...",\n'
            '  "final_positive_prompt": "Perfected prompt with camera, location, lighting Kelvin, clothing seam stress, 1/60s shutter speed, subsurface scattering, authentic skin pores...",\n'
            '  "final_negative_prompt": "blurry, deformed, bad proportions, bad anatomy, fused fingers, asymmetric eyes, extra limbs, low resolution",\n'
            '  "squish_factor": 0.72,\n'
            '  "camera_motion": "Zoom In"\n'
            "}"
        )

        print("\n🧠 [Saluki-27B] 4役CoT思考 ＆ Venice AI風自己批評を実行中...")
        llm = Llama(
            model_path=self.llm_path,
            n_gpu_layers=-int(1),
            n_ctx=4096,
            verbose=False
        )

        full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{self.user_prompt}<|im_end|>\n<|im_start|>assistant\n"
        output = llm(full_prompt, max_tokens=1400, temperature=0.7)

        raw_text = safe_choices_getter(output.get("choices", []))

        del llm
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.queue.put(raw_text)

def run_interactive_session():
    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()

    print("\n" + "═"*65)
    print("   🐺 Project Dystopia: 対話型自己添削＆プロンプト批評機 (Saluki-27B)")
    print("═"*65)

    while True:
        try:
            concept = input("\n💬 日本語でシチュエーションを入力してください (q で終了): ").strip()
            if not concept or concept.lower() == 'q':
                print("テスターセッションを終了します。")
                break

            queue = multiprocessing.Queue()
            p = InteractiveCriticProcess(concept, queue)
            p.start()
            p.join()

            raw_result = queue.get()
            data = bridge.extract_json_by_depth_counter(raw_result)

            print("\n" + "─"*65)
            print("📝 【1. 草案プロンプト (Before)】:")
            print(data.get("raw_draft_positive", ""))
            print("\n🧐 【2. Salukiの自律ダメ出し・批評ログ (Self-Critique)】:")
            print(data.get("self_critique", ""))
            print("\n✨ 【3. 最終修正プロンプト (After: ComfyUIコピペ用)】:")
            print(data.get("final_positive_prompt", ""))
            print(f"\n🎯 【生体力学SQUISH】: {data.get('squish_factor')} / 【推奨カメラ】: {data.get('camera_motion')}")
            print("─"*65)
            print("💡 この【3. 最終修正プロンプト】をスマホブラウザのComfyUI（Port 8188）へ貼り付けて現像してください。")

        except KeyboardInterrupt:
            print("\n中断されました。")
            break
        except Exception as e:
            print(f"\n⚠️ パースまたは実行エラー: {e}")

if __name__ == "__main__":
    run_interactive_session()
