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

# === 思想生成 ===
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

# === 自動評価レイヤー ===
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def extract_score(text):
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    if match:
        return float(match.group(1))
    return None

def evaluate_alignment(prompt_text, image_path):
    vlm_url = "http://localhost:8000/v1/chat/completions"
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
        score = extract_score(score_text)
        return score
    except Exception as e:
        return f"error: {str(e)}"

def update_auto_score(timestamp, score):
    if not os.path.exists(LOG_FILE):
        return "❌ run_log.csv が見つかりません"

    df = pd.read_csv(LOG_FILE)
    if timestamp not in df["timestamp"].values:
        return f"❌ timestamp {timestamp} がログに見つかりません"

    df.loc[df["timestamp"] == timestamp, "auto_score"] = score
    df.to_csv(LOG_FILE, index=False)
    return f"✅ auto_score を更新しました: {score}"

def run_auto_evaluation(timestamp):
    video_path = os.path.join(OUTPUT_DIR, f"prompt_{timestamp}.mp4")
    image_path = os.path.join(FRAME_DIR, f"prompt_{timestamp}.jpg")

    if not extract_frame(video_path, image_path, position="middle"):
        return "❌ フレーム抽出に失敗しました"

    df = pd.read_csv(LOG_FILE)
    row = df[df["timestamp"] == timestamp]
    if row.empty:
        return "❌ 該当するログが見つかりません"

    prompt_text = row.iloc[0]["prompt"]
    score = evaluate_alignment(prompt_text, image_path)
    if isinstance(score, str) and score.startswith("error"):
        return score

    return update_auto_score(timestamp, score)

# === 自己進化ループ ===
def generate_variant_from_top_score(top_n=3, temperature=0.9):
    if not os.path.exists(LOG_FILE):
        return "❌ run_log.csv が見つかりません"

    df = pd.read_csv(LOG_FILE)
    df = df.dropna(subset=["auto_score"])
    df["auto_score"] = pd.to_numeric(df["auto_score"], errors="coerce")
    df = df.sort_values(by="auto_score", ascending=False).head(top_n)

    if df.empty:
        return "❌ 評価済みの思想が見つかりません"

    base_prompt = df.iloc[0]["prompt"]

    payload = {
        "model": "chronos-hermes-13b",
        "messages": [
            {"role": "system", "content": "あなたは映像監督です。以下の思想をもとに、少し変化を加えた新しい思想を1つ生成してください。"},
            {"role": "user", "content": base_prompt}
        ],
        "temperature": temperature
    }

    try:
        response = requests.post(VLLM_URL, json=payload).json()
        new_prompt = response['choices'][0]['message']['content']
        return new_prompt
    except Exception as e:
        return f"❌ LLMエラー: {str(e)}"

def run_self_evolution():
    new_prompt = generate_variant_from_top_score()
    if new_prompt.startswith("❌"):
        return new_prompt

    thought_json = generate_thought(new_prompt)
    try:
        thought = json.loads(thought_json)
    except:
        return "❌ 構造化に失敗しました"

    status = queue_video_generation(thought_json)
    if not status.startswith("✅"):
        return status

    match = re.search(r"prompt_(\d{8}_\d{6})\.json", status)
    if not match:
        return "❌ timestamp の抽出に失敗しました"
    timestamp = match.group(1)

    result = run_auto_evaluation(timestamp)
    return f"🧠 新しい思想を生成・評価しました\n\n{new_prompt}\n\n{result}"
# === ComfyUI 実行ロジック ===
def queue_video_generation(thought_json_str):
    try:
        thought = json.loads(thought_json_str)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        payload_path = os.path.join(PAYLOAD_DIR, f"prompt_{timestamp}.json")

        with open(WORKFLOW_TEMPLATE, "r") as f:
            workflow = json.load(f)

        with open(MAPPING_CONFIG_PATH, "r") as f:
            mapping_config = json.load(f)
        workflow = apply_mapping(thought, workflow, mapping_config)

        with open(payload_path, "w") as f:
            json.dump(workflow, f, indent=2)

        requests.post(COMFY_URL, json=workflow)

        log_entry = {
            "timestamp": timestamp,
            "prompt": thought.get("prompt", ""),
            "intensity": thought.get("intensity", ""),
            "chaos": thought.get("chaos", ""),
            "motion_intent": thought.get("motion_intent", ""),
            "visual_persistence": thought.get("visual_persistence", ""),
            "guidance_scale": 1.0 + thought.get("intensity", 0.5) * 7.0,
            "seed": int(1000 + thought.get("chaos", 0.5) * 1000),
            "segment_index": 0,
            "user_score": "",
            "auto_score": ""
        }

        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
            df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([log_entry])
        df.to_csv(LOG_FILE, index=False)

        return f"✅ 映像生成をキューに追加しました: prompt_{timestamp}.json"
    except Exception as e:
        return f"❌ エラー: {str(e)}"

# === ログ・ギャラリー ===
def load_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    else:
        return pd.DataFrame()

def list_payloads():
    files = [f for f in os.listdir(PAYLOAD_DIR) if f.endswith(".json")]
    return sorted(files, reverse=True)

def load_payload(filename):
    path = os.path.join(PAYLOAD_DIR, filename)
    try:
        with open(path, "r") as f:
            data = json.load(f)
        prompt = ""
        intensity = 0.5
        chaos = 0.5
        motion_intent = ""
        visual_persistence = 0.5
        for node in data["nodes"]:
            if node["type"] == "CLIPTextEncode":
                prompt = node["inputs"].get("text", "")
            if node["type"] == "LTXVSampler":
                gs = node["properties"].get("guidance_scale", 5.0)
                sd = node["properties"].get("seed", 1234)
                intensity = round((gs - 1.0) / 7.0, 2)
                chaos = round((sd - 1000) / 1000.0, 2)
        thought = {
            "prompt": prompt,
            "intensity": intensity,
            "chaos": chaos,
            "motion_intent": motion_intent,
            "visual_persistence": visual_persistence
        }
        return json.dumps(thought, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# === GUI構築 ===
with gr.Blocks(title="Project Dystopia - Phase VIII Interface", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧠 Project Dystopia: Phase VIII Control Center")

    with gr.Tab("思想生成 & 映像化"):
        with gr.Row():
            with gr.Column(scale=1):
                user_input = gr.Textbox(label="思想（入力）", placeholder="静かな森の中で、時間が溶けていく...", lines=5)
                gen_btn = gr.Button("思想を構造化する", variant="primary")
            with gr.Column(scale=1):
                thought_editor = gr.Code(label="構造化データ (JSON)", language="json", interactive=True)
                run_btn = gr.Button("映像生成開始 (LTX-2)", variant="stop")
                status = gr.Textbox(label="ステータス", interactive=False)

    with gr.Tab("アーカイブ & ログ"):
        with gr.Row():
            with gr.Column(scale=1):
                log_table = gr.DataFrame(label="生成ログ (run_log.csv)")
                refresh_btn = gr.Button("ログを更新")
            with gr.Column(scale=1):
                payload_selector = gr.Dropdown(label="過去の思想を選択", choices=[], interactive=True)
                load_btn = gr.Button("選択した思想を読み込む")

    with gr.Tab("自動評価"):
        with gr.Row():
            eval_selector = gr.Dropdown(label="評価対象のtimestampを選択", choices=[], interactive=True)
            eval_btn = gr.Button("自動評価を実行")
            eval_result = gr.Textbox(label="評価結果", interactive=False)

    with gr.Tab("自己進化"):
        evolve_btn = gr.Button("自己進化ループを1回実行")
        evolve_output = gr.Textbox(label="進化ログ", lines=10)

    # イベント連携
    gen_btn.click(generate_thought, inputs=[user_input], outputs=[thought_editor])
    run_btn.click(queue_video_generation, inputs=[thought_editor], outputs=[status])
    refresh_btn.click(load_log, outputs=[log_table])
    refresh_btn.click(list_payloads, outputs=[payload_selector])
    refresh_btn.click(list_payloads, outputs=[eval_selector])
    load_btn.click(load_payload, inputs=[payload_selector], outputs=[thought_editor])
    eval_btn.click(run_auto_evaluation, inputs=[eval_selector], outputs=[eval_result])
    evolve_btn.click(run_self_evolution, outputs=[evolve_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
