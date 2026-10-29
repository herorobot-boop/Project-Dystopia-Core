import os
import re
import json
import time
import shutil
import requests
from pathlib import Path
from typing import Tuple, Dict, Any

WORKSPACE_DIR = Path("/workspace")
COMFY_DIR = WORKSPACE_DIR / "ComfyUI"
INPUT_DIR = COMFY_DIR / "input"
OUTPUT_DIR = COMFY_DIR / "output"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def align_resolution_16px(width: int, height: int) -> Tuple[int, int]:
    aligned_w = (int(width) // 16) * 16
    aligned_h = (int(height) // 16) * 16
    return max(16, aligned_w), max(16, aligned_h)

class ComfyAPIBridge:
    def __init__(self, host="127.0.0.1", port=8188):
        self.server_address = f"{host}:{port}"
        self.server_url = f"http://{self.server_address}"

    def purge_comfyui_vram_cache(self):
        try:
            url = f"{self.server_url}/free"
            res = requests.post(url, json={"unload_models": True, "free_memory": True}, timeout=5)
            if res.status_code == 200:
                print("🧹 [VRAM Interlock] ComfyUI VRAM パージ成功。")
                time.sleep(2.0)
        except Exception as e:
            print(f"⚠️ [VRAM Interlock] Skip /free API: {e}")

    def _backtrack_to_clip_encode(self, workflow: dict, start_node_id: str, slot_type: str = "positive", visited: set = None) -> str:
        if visited is None:
            visited = set()
        if start_node_id in visited or start_node_id not in workflow:
            return None
        visited.add(start_node_id)

        current_node = workflow.get(start_node_id, {})
        class_type = current_node.get("class_type", "")
        inputs = current_node.get("inputs", {})

        if class_type == "CLIPTextEncode" or "text" in inputs:
            return start_node_id

        if slot_type in inputs:
            conn = inputs.get(slot_type)
            if isinstance(conn, list) and len(conn) > int(0):
                upstream_node_id, *_ = conn
                return self._backtrack_to_clip_encode(workflow, str(upstream_node_id), slot_type, visited)
        return None

    def find_prompt_nodes_smart(self, workflow: dict) -> Tuple[str, str, str]:
        pos_id, neg_id, ksampler_id = None, None, None
        for node_id, node in workflow.items():
            if isinstance(node, dict) and ("KSampler" in node.get("class_type", "") or "Sampler" in node.get("class_type", "")):
                ksampler_id = node_id
                inputs = node.get("inputs", {})
                if "positive" in inputs and isinstance(inputs["positive"], list) and len(inputs["positive"]) > int(0):
                    up_pos, *_ = inputs["positive"]
                    pos_id = self._backtrack_to_clip_encode(workflow, str(up_pos), "positive")
                if "negative" in inputs and isinstance(inputs["negative"], list) and len(inputs["negative"]) > int(0):
                    up_neg, *_ = inputs["negative"]
                    neg_id = self._backtrack_to_clip_encode(workflow, str(up_neg), "negative")
                if pos_id and neg_id:
                    break

        if not pos_id or not neg_id:
            clip_nodes = [nid for nid, n in workflow.items() if isinstance(n, dict) and n.get("class_type") == "CLIPTextEncode"]
            if len(clip_nodes) >= 2:
                pos_id, neg_id = clip_nodes[int(0)], clip_nodes[1]
            elif len(clip_nodes) == 1:
                pos_id, neg_id = clip_nodes[int(0)], "7"
            else:
                pos_id, neg_id = "6", "7"

        return pos_id, neg_id, ksampler_id

    def extract_json_by_depth_counter(self, text: str) -> dict:
        code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if code_block:
            clean_str = code_block.group(int(0)).replace(" ", " ")
            clean_str = re.sub(r',\s*([\}\]])', r'\1', clean_str)
            return json.loads(clean_str)

        start_idx = text.find('{')
        if start_idx == -int(1):
            raise ValueError("有効なJSON開始括弧が見つかりません。")

        depth = int(0)
        candidate = None
        for i, char in enumerate(text):
            if char == '{':
                depth += int(1)
            elif char == '}':
                depth -= int(1)
                if depth == int(0):
                    candidate = text[start_idx:i+int(1)]
                    break

        if not candidate:
            raise ValueError(f"有効なJSON構造が抽出できませんでした: {text[:200]}")

        clean_str = candidate.replace(" ", " ")
        clean_str = re.sub(r',\s*([\}\]])', r'\1', clean_str)
        return json.loads(clean_str)

    def dispatch_and_wait_media(self, workflow: dict, timeout: int = 360) -> str:
        res = requests.post(f"{self.server_url}/prompt", json={"prompt": workflow}, timeout=10)
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]
        print(f"🚀 [ComfyUI API] Prompt ID: {prompt_id} 射出完了。レンダリング監視中...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                hist_res = requests.get(f"{self.server_url}/history/{prompt_id}", timeout=5)
                if hist_res.status_code == 200:
                    history_data = hist_res.json()
                    if prompt_id in history_data:
                        outputs = history_data[prompt_id].get("outputs", {})
                        for node_id, node_output in outputs.items():
                            for media_key in ("images", "gifs", "videos"):
                                if media_key in node_output and len(node_output[media_key]) > int(0):
                                    filename = node_output[media_key][int(0)]["filename"]
                                    print(f"✅ [Media Handover] レンダリング完了検知 ({media_key}): {filename}")
                                    return filename
            except Exception:
                pass
            time.sleep(2.0)

        raise TimeoutError(f"⏰ [Timeout] Prompt ID: {prompt_id} が {timeout} 秒以内に完了しませんでした。")

    def sync_output_to_input(self, filename: str):
        src = OUTPUT_DIR / filename
        dst = INPUT_DIR / filename
        if src.exists():
            shutil.copy(src, dst)
            print(f"🔄 [Dir Sync] {filename} を output/ から input/ へ同期完了。")
        else:
            raise FileNotFoundError(f"同期元ファイルが存在しません: {src}")

    def inject_image_to_workflow(self, workflow: dict, image_filename: str) -> dict:
        target_id = None
        for node_id, node in workflow.items():
            if isinstance(node, dict):
                if node.get("_meta", {}).get("title") == "Load_Source_Image" or node.get("class_type") == "LoadImage":
                    target_id = node_id
                    break

        if target_id and target_id in workflow:
            workflow[target_id]["inputs"]["image"] = image_filename
            print(f"🔗 [Image Handover] 動画ノード(ID: {target_id}) へ 『{image_filename}』 を完全接続。")
        else:
            print(f"⚠️ [Handover Warning] 動画ワークフロー内に LoadImage ノードを特定できませんでした。")

        return workflow

    def inject_dynamic_parameters(self, workflow: dict, prompt_data: dict) -> dict:
        pos_id, neg_id, ksampler_id = self.find_prompt_nodes_smart(workflow)

        if pos_id in workflow:
            workflow[pos_id]["inputs"]["text"] = prompt_data.get("positive_prompt", "")
        if neg_id in workflow:
            workflow[neg_id]["inputs"]["text"] = prompt_data.get("negative_prompt", "")

        if ksampler_id and ksampler_id in workflow:
            if prompt_data.get("is_distilled_model", True):
                workflow[ksampler_id]["inputs"]["steps"] = 8
                workflow[ksampler_id]["inputs"]["cfg"] = 1.0
                denoise_val = min(0.50, max(0.35, float(prompt_data.get("squish_factor", 0.42))))
                workflow[ksampler_id]["inputs"]["denoise"] = denoise_val

        for nid, node in workflow.items():
            if isinstance(node, dict):
                ctype = node.get("class_type", "")
                if ctype == "WanCameraEmbedding":
                    inputs = node.get("inputs", {})
                    orig_w = inputs.get("width", 768)
                    orig_h = inputs.get("height", 1280)
                    align_w, align_h = align_resolution_16px(orig_w, orig_h)

                    inputs["camera_motion"] = prompt_data.get("camera_motion", "Zoom In")
                    inputs["speed"] = float(1.2)
                    inputs["width"] = align_w
                    inputs["height"] = align_h
                    inputs["length"] = 81
                    print(f"🎥 [Wan Camera] Single float speed (1.2) & Motion ({inputs['camera_motion']}) 固定適用")
                elif "TeaCache" in ctype or ctype == "WanTeaCache":
                    node["inputs"]["rel_l1_thresh"] = 0.18

        return workflow
