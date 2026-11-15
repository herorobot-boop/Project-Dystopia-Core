import os
import re
import json
import time
import shutil
import requests
from pathlib import Path
from typing import Tuple

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
            res = requests.post(f"{self.server_url}/free",
                                json={"unload_models": True, "free_memory": True}, timeout=5)
            if res.status_code == 200:
                print("🧹 [VRAM Interlock] パージ成功。")
                time.sleep(2.0)
        except Exception as e:
            print(f"⚠️ [VRAM Interlock] Skip /free API: {e}")

    def _backtrack_to_clip_encode(self, workflow: dict, start_node_id: str,
                                  slot_type: str = "positive", visited: set = None) -> str:
        if visited is None:
            visited = set()
        if start_node_id in visited or start_node_id not in workflow:
            return None
        visited.add(start_node_id)

        current = workflow.get(start_node_id, {})
        class_type = current.get("class_type", "")
        inputs = current.get("inputs", {})

        if class_type == "CLIPTextEncode" or "text" in inputs:
            return start_node_id

        if slot_type in inputs:
            conn = inputs.get(slot_type)
            if isinstance(conn, list) and len(conn) > 0:
                upstream, *_ = conn
                return self._backtrack_to_clip_encode(workflow, str(upstream), slot_type, visited)
        return None

    def find_prompt_nodes_smart(self, workflow: dict) -> Tuple[str, str, str]:
        pos_id, neg_id, ksampler_id = None, None, None
        for node_id, node in workflow.items():
            if isinstance(node, dict) and ("KSampler" in node.get("class_type", "")
                                           or "Sampler" in node.get("class_type", "")):
                ksampler_id = node_id
                inputs = node.get("inputs", {})
                if isinstance(inputs.get("positive"), list) and inputs["positive"]:
                    up_pos, *_ = inputs["positive"]
                    pos_id = self._backtrack_to_clip_encode(workflow, str(up_pos), "positive")
                if isinstance(inputs.get("negative"), list) and inputs["negative"]:
                    up_neg, *_ = inputs["negative"]
                    neg_id = self._backtrack_to_clip_encode(workflow, str(up_neg), "negative")
                if pos_id and neg_id:
                    break

        if not pos_id or not neg_id:
            clip_nodes = [nid for nid, n in workflow.items()
                          if isinstance(n, dict) and n.get("class_type") == "CLIPTextEncode"]
            if len(clip_nodes) >= 2:
                pos_id, neg_id = clip_nodes[0], clip_nodes[1]
            elif len(clip_nodes) == 1:
                pos_id, neg_id = clip_nodes[0], "7"
            else:
                pos_id, neg_id = "6", "7"

        return pos_id, neg_id, ksampler_id

    def extract_json_by_depth_counter(self, text: str) -> dict:
        code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if code_block:
            clean_str = re.sub(r',\s*([\}\]])', r'\1', code_block.group(0))
            return json.loads(clean_str)

        start_idx = text.find('{')
        if start_idx == -1:
            raise ValueError("JSON開始括弧が見つかりません。")

        depth = 0
        candidate = None
        for i, char in enumerate(text[start_idx:], start=start_idx):
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    candidate = text[start_idx:i + 1]
                    break

        if not candidate:
            raise ValueError(f"JSON構造を抽出できません: {text[:200]}")

        clean_str = re.sub(r',\s*([\}\]])', r'\1', candidate)
        return json.loads(clean_str)

    def _report_prompt_error(self, body: str) -> str:
        """ComfyUI の 400 応答から原因ノードを読み取って要約する。"""
        try:
            data = json.loads(body)
        except Exception:
            return body[:800]

        parts = []
        node_errors = data.get("node_errors") or {}
        for node_id, info in node_errors.items():
            ctype = info.get("class_type", "?")
            for err in info.get("errors", []):
                parts.append(f"ノード{node_id}({ctype}): {err.get('message')} / {err.get('details')}")
        if not parts:
            parts.append(data.get("error", {}).get("message", body[:400]))
        return "\n".join(parts) if parts else body[:800]

    def dispatch_and_wait_media(self, workflow: dict, timeout: int = 360) -> str:
        res = requests.post(f"{self.server_url}/prompt", json={"prompt": workflow}, timeout=15)
        if res.status_code != 200:
            detail = self._report_prompt_error(res.text)
            raise RuntimeError(f"/prompt 拒否 {res.status_code}\n{detail}")

        prompt_id = res.json()["prompt_id"]
        print(f"🚀 [API] Prompt ID: {prompt_id} 投入。監視中...")

        start = time.time()
        while time.time() - start < timeout:
            try:
                hist = requests.get(f"{self.server_url}/history/{prompt_id}", timeout=5)
                if hist.status_code == 200:
                    data = hist.json()
                    if prompt_id in data:
                        entry = data[prompt_id]
                        status = entry.get("status", {})
                        if status.get("status_str") == "error":
                            msgs = []
                            for msg in status.get("messages", []):
                                if isinstance(msg, list) and len(msg) > 1:
                                    msgs.append(str(msg[1])[:300])
                            raise RuntimeError("実行時エラー\n" + "\n".join(msgs))

                        outputs = entry.get("outputs", {})
                        for node_output in outputs.values():
                            for key in ("images", "gifs", "videos"):
                                if key in node_output and node_output[key]:
                                    filename = node_output[key][0]["filename"]
                                    print(f"✅ [Handover] 完了 ({key}): {filename}")
                                    return filename
            except RuntimeError:
                raise
            except Exception:
                pass
            time.sleep(2.0)

        raise TimeoutError(f"⏰ Prompt ID: {prompt_id} が {timeout} 秒で完了せず")

    def sync_output_to_input(self, filename: str):
        src = OUTPUT_DIR / filename
        dst = INPUT_DIR / filename
        if not src.exists():
            raise FileNotFoundError(f"同期元が無い: {src}")
        shutil.copy(src, dst)
        print(f"🔄 [Dir Sync] {filename} を input/ へ同期。")

    def inject_image_to_workflow(self, workflow: dict, image_filename: str) -> dict:
        target_id = None
        for node_id, node in workflow.items():
            if isinstance(node, dict) and node.get("class_type") == "LoadImage":
                target_id = node_id
                break
        if target_id:
            workflow[target_id]["inputs"]["image"] = image_filename
            print(f"🔗 [Handover] LoadImage({target_id}) へ {image_filename}")
        else:
            print("⚠️ [Handover] LoadImage ノードが見つからない")
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

        for node in workflow.values():
            if not isinstance(node, dict):
                continue
            ctype = node.get("class_type", "")
            if ctype == "WanCameraEmbedding":
                inputs = node.get("inputs", {})
                w, h = align_resolution_16px(inputs.get("width", 768), inputs.get("height", 1280))
                inputs["camera_motion"] = prompt_data.get("camera_motion", "Zoom In")
                inputs["speed"] = 1.2
                inputs["width"] = w
                inputs["height"] = h
                inputs["length"] = 81
            elif "TeaCache" in ctype or ctype == "WanTeaCache":
                node["inputs"]["rel_l1_thresh"] = 0.18

        return workflow
