import gradio as gr
import json
import requests
import os
import pandas as pd
from datetime import datetime
import math

# === 設定 ===
VLLM_URL = "http://localhost:8000/v1/chat/completions"
COMFY_URL = "http://localhost:8188/prompt"
PAYLOAD_DIR = "/workspace/gdrive/MyDrive/Project-Dystopia/RunPayloads"
LOG_FILE = "/workspace/run_log.csv"
WORKFLOW_TEMPLATE = "/workspace/Project-Dystopia/templates/ltx2_infinity_template.json"
MAPPING_CONFIG_PATH = "/workspace/Project-Dystopia/config/mapping_config.json"

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

# === ComfyUI 実行ロジック ===
def queue_video_generation(thought_json_str):
    try:
        thought = json.loads(thought_json_str)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        payload_path = os.path.join(PAYLOAD_DIR, f"prompt_{timestamp}.json")

        # テンプレート読み込み
        with open(WORKFLOW_TEMPLATE, "r") as f:
            workflow = json.load(f)

        # マッピング設定の読み込みと適用
        with open(MAPPING_CONFIG_PATH, "r") as f:
            mapping_config = json.load(f)
        workflow = apply_mapping(thought, workflow, mapping_config)

        # 保存
        with open(payload_path, "w") as f:
            json.dump(workflow, f, indent=2)

        # ComfyUIに送信
        requests.post(COMFY_URL, json=workflow)

        # ログ記録
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

        return f"✅ 映像生成をキューに追加しました: {os.path.basename(payload_path)}"
    except Exception as e:
        return f"❌ エラー: {str(e)}"

# === ログ読み込み ===
def load_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    else:
        return pd.DataFrame()

# === RunPayloads ギャラリー ===
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

# === GUI 構築 ===
with gr.Blocks(title="Project Dystopia - Phase VII Interface", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧠 Project Dystopia: Phase VII Control Center")

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

    # イベント連携
    gen_btn.click(generate_thought, inputs=[user_input], outputs=[thought_editor])
    run_btn.click(queue_video_generation, inputs=[thought_editor], outputs=[status])
    refresh_btn.click(load_log, outputs=[log_table])
    refresh_btn.click(list_payloads, outputs=[payload_selector])
    load_btn.click(load_payload, inputs=[payload_selector], outputs=[thought_editor])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
