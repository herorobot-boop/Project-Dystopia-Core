import gradio as gr
import json
import re
from datetime import datetime
from core.thought_engine import generate_thought, fuse_thoughts, generate_variant_from_top_score
from core.mapping import apply_mapping
from core.io_utils import save_payload, save_log_entry, load_log, load_payload
from core.evaluator import run_auto_evaluation
import os
import pandas as pd
import requests

# === 設定 ===
VLLM_URL = "http://localhost:8000/v1/chat/completions"
COMFY_URL = "http://localhost:8188/prompt"
PAYLOAD_DIR = "/workspace/gdrive/MyDrive/Project-Dystopia/RunPayloads"
LOG_FILE = "/workspace/run_log.csv"
WORKFLOW_TEMPLATE = "/workspace/Project-Dystopia/templates/ltx2_infinity_template.json"
MAPPING_CONFIG_PATH = "/workspace/Project-Dystopia/config/mapping_config.json"
OUTPUT_DIR = "/workspace/outputs"
FRAME_DIR = "/workspace/frames"

# === ComfyUI 実行ロジック ===
def queue_video_generation(thought):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload_path = os.path.join(PAYLOAD_DIR, f"prompt_{timestamp}.json")

    with open(WORKFLOW_TEMPLATE, "r") as f:
        workflow = json.load(f)
    with open(MAPPING_CONFIG_PATH, "r") as f:
        mapping_config = json.load(f)

    workflow = apply_mapping(thought, workflow, mapping_config)
    save_payload(payload_path, workflow)
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
    save_log_entry(LOG_FILE, log_entry)
    return f"✅ 映像生成をキューに追加しました: prompt_{timestamp}.json", timestamp

# === 自己進化ループ ===
def run_self_evolution():
    new_prompt = generate_variant_from_top_score()
    if new_prompt.startswith("❌"):
        return new_prompt

    thought = generate_thought(new_prompt)
    if "error" in thought:
        return f"❌ 構造化に失敗しました: {thought['error']}"

    status, timestamp = queue_video_generation(thought)
    if not status.startswith("✅"):
        return status

    result = run_auto_evaluation(timestamp, LOG_FILE, OUTPUT_DIR, FRAME_DIR)
    return f"🧠 新しい思想を生成・評価しました\n\n{new_prompt}\n\n{result}"

# === 交配ループ ===
def run_cross_breed(self_prompt, external_prompt):
    fused_prompt = fuse_thoughts(self_prompt, external_prompt)
    if fused_prompt.startswith("❌"):
        return fused_prompt

    thought = generate_thought(fused_prompt)
    if "error" in thought:
        return f"❌ 構造化に失敗しました: {thought['error']}"

    status, timestamp = queue_video_generation(thought)
    if not status.startswith("✅"):
        return status

    result = run_auto_evaluation(timestamp, LOG_FILE, OUTPUT_DIR, FRAME_DIR)
    return f"🧬 交配思想を生成・評価しました\n\n{fused_prompt}\n\n{result}"

# === GUI構築 ===
with gr.Blocks(title="Project Dystopia Interface", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧠 Project Dystopia: Modular Interface")

    with gr.Tab("思想生成 & 映像化"):
        user_input = gr.Textbox(label="思想（入力）", lines=4)
        gen_btn = gr.Button("構造化")
        thought_editor = gr.Code(label="構造化データ", language="json", interactive=True)
        run_btn = gr.Button("映像生成")
        status = gr.Textbox(label="ステータス", interactive=False)

    with gr.Tab("ログ"):
        log_table = gr.DataFrame(label="生成ログ")
        refresh_btn = gr.Button("ログ更新")

    with gr.Tab("自動評価"):
        eval_selector = gr.Dropdown(label="timestamp選択", choices=[], interactive=True)
        eval_btn = gr.Button("評価実行")
        eval_result = gr.Textbox(label="評価結果")

    with gr.Tab("自己進化"):
        evolve_btn = gr.Button("自己進化ループ")
        evolve_output = gr.Textbox(label="進化ログ", lines=10)

    with gr.Tab("交配"):
        self_input = gr.Textbox(label="自己思想", lines=3)
        external_input = gr.Textbox(label="外部思想", lines=3)
        cross_btn = gr.Button("交配して評価")
        cross_result = gr.Textbox(label="交配ログ", lines=10)

    # イベント連携
    gen_btn.click(lambda x: json.dumps(generate_thought(x), indent=2), inputs=[user_input], outputs=[thought_editor])
    run_btn.click(lambda x: queue_video_generation(json.loads(x))[0], inputs=[thought_editor], outputs=[status])
    refresh_btn.click(lambda: load_log(LOG_FILE), outputs=[log_table])
    refresh_btn.click(lambda: os.listdir(PAYLOAD_DIR), outputs=[eval_selector])
    eval_btn.click(lambda ts: run_auto_evaluation(ts, LOG_FILE, OUTPUT_DIR, FRAME_DIR), inputs=[eval_selector], outputs=[eval_result])
    evolve_btn.click(run_self_evolution, outputs=[evolve_output])
    cross_btn.click(run_cross_breed, inputs=[self_input, external_input], outputs=[cross_result])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
