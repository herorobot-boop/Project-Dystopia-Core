import gradio as gr
import json
import requests
import os
import pandas as pd
from datetime import datetime
import math
import base64
import re
from tools.extract_frame import extract_frame  # 映像→画像抽出スクリプト

# === 設定 ===
VLLM_URL = "http://localhost:8000/v1/chat/completions"
COMFY_URL = "http://localhost:8188/prompt"
PAYLOAD_DIR = "/workspace/gdrive/MyDrive/Project-Dystopia/RunPayloads"
LOG_FILE = "/workspace/run_log.csv"
WORKFLOW_TEMPLATE = "/workspace/Project-Dystopia/templates/ltx2_infinity_template.json"
MAPPING_CONFIG_PATH = "/workspace/Project-Dystopia/config/mapping_config.json"
OUTPUT_DIR = "/workspace/outputs"
FRAME_DIR = "/workspace/frames"

# === LLM 思想生成ロジック ===
def generate_thought(user_input):
    payload = {
        "model": "chronos-hermes-13b",
        "messages": [
            {"role": "system", "content": "あなたは映像監督です。入力された思想を構造化JSONで出力してください。出力形式は {\"prompt\": ..., \"intensity\": ..., \"chaos\": ..., \"motion_intent\": ..., \"visual_persistence\": ...} の形式でお願いします。"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.8
    }
    try:
        response = requests.post(VLLM_URL, json=payload).json()
        content = response['choices'][0]['message']['content']
        parsed = json.loads(content)
        return json.dumps(parsed, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# === マッピングエンジン ===
def apply_mapping(thought, workflow, mapping_config):
    context = {**thought}
    for key, rule in mapping_config.items():
        formula = rule["formula"]
        try:
            value = eval(formula, {"__builtins__": {}, "int": int, "round": round, "math": math}, context)
        except Exception as e:
            print(f"[Mapping Error] {key}: {e}")
            continue

        for node in workflow["nodes"]:
            if node["type"] == rule["target_node_type"]:
                fields = rule["target_field"].split(".")
                target = node
                for f in fields[:-1]:
                    target = target.setdefault(f, {})
                target[fields[-1]] = value
    return workflow
