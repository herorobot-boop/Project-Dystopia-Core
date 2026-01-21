# core/thought_engine.py

import json
import requests
import re
from datetime import datetime
from core.mapping import apply_mapping
from core.io_utils import save_log_entry, save_payload
from config import VLLM_URL, WORKFLOW_TEMPLATE, MAPPING_CONFIG_PATH, COMFY_URL

def generate_thought(user_input, temperature=0.8):
    payload = {
        "model": "chronos-hermes-13b",
        "messages": [
            {"role": "system", "content": "あなたは映像監督です。入力された思想を構造化JSONで出力してください。出力形式は {...}"},
            {"role": "user", "content": user_input}
        ],
        "temperature": temperature
    }
    try:
        response = requests.post(VLLM_URL, json=payload).json()
        content = response['choices'][0]['message']['content']
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        return {"error": str(e)}

def fuse_thoughts(self_prompt, external_prompt, temperature=0.85):
    payload = {
        "model": "chronos-hermes-13b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "あなたは映像監督です。以下の2つの思想を受け取り、それらを融合させた新しい思想を1つ生成してください。\n\n"
                    f"自己思想: 「{self_prompt}」\n"
                    f"外部思想: 「{external_prompt}」\n\n"
                    "→ 出力形式: 新しい思想（自然文1文）"
                )
            }
        ],
        "temperature": temperature
    }

    try:
        response = requests.post(VLLM_URL, json=payload).json()
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ LLMエラー: {str(e)}"
