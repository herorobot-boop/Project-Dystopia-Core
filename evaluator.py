# core/evaluator.py

import base64
import re
import requests
from core.io_utils import update_log_score
from tools.extract_frame import extract_frame
import os
import pandas as pd

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def extract_score(text):
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    if match:
        return float(match.group(1))
    return None

def evaluate_alignment(prompt_text, image_path, vlm_url="http://localhost:8000/v1/chat/completions"):
    image_b64 = encode_image_to_base64(image_path)
    payload = {
        "model": "llava",
        "messages": [
            {"role": "user", "content": f"この画像は次の説明とどれくらい一致していますか？説明: {prompt_text}。10点満点で評価してください。"}
        ],
        "temperature": 0.2,
        "max_tokens": 100,
        "image": image_b64
    }

    try:
        response = requests.post(vlm_url, json=payload).json()
        score_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        return extract_score(score_text)
    except Exception as e:
        return f"error: {str(e)}"

def run_auto_evaluation(timestamp, log_file, output_dir, frame_dir):
    video_path = os.path.join(output_dir, f"prompt_{timestamp}.mp4")
    image_path = os.path.join(frame_dir, f"prompt_{timestamp}.jpg")

    if not extract_frame(video_path, image_path, position="middle"):
        return "❌ フレーム抽出に失敗しました"

    df = pd.read_csv(log_file)
    row = df[df["timestamp"] == timestamp]
    if row.empty:
        return "❌ 該当するログが見つかりません"

    prompt_text = row.iloc[0]["prompt"]
    score = evaluate_alignment(prompt_text, image_path)
    if isinstance(score, str) and score.startswith("error"):
        return score

    success = update_log_score(log_file, timestamp, score)
    return f"✅ auto_score を更新しました: {score}" if success else "❌ スコア更新に失敗しました"
