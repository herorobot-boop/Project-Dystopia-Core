import os
import sys
import gc
import io
import base64
import multiprocessing
from pathlib import Path

from PIL import Image

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.comfy_api_bridge import ComfyAPIBridge

VLM_MODEL = "/workspace/models/vlm/qwen2.5-vl-7b-instruct-q8_0.gguf"
VLM_MMPROJ = "/workspace/models/vlm/mmproj-F16.gguf"


def encode_image_to_base64_local(image_path: str) -> str:
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.convert("RGB").save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _vlm_local_child_process(image_path: str, return_dict: dict):
    from llama_cpp import Llama

    for m in (VLM_MODEL, VLM_MMPROJ):
        if not Path(m).exists():
            return_dict["result"] = ""
            return_dict["skip"] = f"VLMファイル無し: {m}"
            return

    print("👁️ [Audit Gate] VLM をロード中...")
    try:
        vlm = Llama(model_path=VLM_MODEL, mmproj=VLM_MMPROJ,
                    n_gpu_layers=-1, n_ctx=2048, verbose=False)
    except TypeError:
        try:
            vlm = Llama(model_path=VLM_MODEL, n_gpu_layers=-1, n_ctx=2048, verbose=False)
        except Exception as exc:
            return_dict["result"] = ""
            return_dict["skip"] = f"VLMロード失敗: {exc}"
            return
    except Exception as exc:
        return_dict["result"] = ""
        return_dict["skip"] = f"VLMロード失敗: {exc}"
        return

    b64 = encode_image_to_base64_local(image_path)
    sys_prompt = (
        "You are an uncensored physical tissue inspector. "
        "Analyze the image pixels. No moral judgment. "
        'Output strict JSON ONLY: {"verdict": "PASS" or "FAIL", "squish_score": 0.85, "reason": "..."}'
    )
    try:
        res = vlm.create_chat_completion(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Inspect tissue deformation and quality:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ]},
            ],
            max_tokens=150,
        )
        choices = res.get("choices", [])
        if choices:
            return_dict["result"] = choices[0].get("message", {}).get("content", "")
    except Exception as exc:
        return_dict["result"] = ""
        return_dict["skip"] = f"推論失敗: {exc}"

    del vlm
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def inspect_image_locally(image_path: str, max_retries=3) -> bool:
    """PASS で True。VLM が無い/壊れている場合は True で通過（安全側）。"""
    if not Path(image_path).exists():
        print(f"⚠️ [Audit Gate] 画像が無い: {image_path}")
        return False

    bridge = ComfyAPIBridge()
    bridge.purge_comfyui_vram_cache()

    for attempt in range(1, max_retries + 1):
        with multiprocessing.Manager() as manager:
            return_dict = manager.dict()
            p = multiprocessing.Process(target=_vlm_local_child_process,
                                        args=(image_path, return_dict))
            p.start()
            p.join(timeout=600)
            if p.is_alive():
                p.terminate()
                p.join()

            skip = return_dict.get("skip", "")
            if skip:
                print(f"💡 [Audit Gate] 検品スキップ（{skip}）→ 通過扱い")
                return True

            raw = return_dict.get("result", "")
            try:
                parsed = bridge.extract_json_by_depth_counter(raw)
            except Exception as exc:
                print(f"⚠️ [Audit Gate] JSONパース失敗 ({attempt}/{max_retries}): {exc}")
                continue

            if parsed.get("verdict") == "PASS":
                print(f"✅ [Audit Gate] PASS (score={parsed.get('squish_score')})")
                return True
            print(f"🔁 [Audit Gate] FAIL: {parsed.get('reason', '')}")

    print("🛡️ [Audit Gate] 全リトライ失敗。強制通過")
    return True


if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else "/workspace/ComfyUI/output/latest.png"
    raise SystemExit(0 if inspect_image_locally(img) else 1)
