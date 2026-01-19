import gradio as gr
from prompt_engine_v2_chronos import ChronosLLM
from chronos_mapper_v3_2 import ChronosMapperV3_2
from prompt_builder import build_prompt
import json
import os
from datetime import datetime

# === 設定 ===
LLM_ENDPOINT = "http://localhost:8000/v1/chat/completions"
SYSTEM_PROMPT = "system_prompt.txt"
COT_PROTOCOL = "cot_protocol.txt"
TAG_DB = "structure_tags.json"
MAPPED_DIR = "mapped/"
OUTPUT_DIR = "RunPayloads/"

# === 初期化 ===
llm = ChronosLLM(LLM_ENDPOINT, SYSTEM_PROMPT, COT_PROTOCOL)
mapper = ChronosMapperV3_2(template_path=TAG_DB, output_dir=MAPPED_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_all(user_instruction, tags):
    # 1. 思想生成
    llm_output = llm.generate_prompt(scene_seed="GUI構成", tags=tags.split(","), user_instruction=user_instruction)

    # 2. 構造変換
    scene_json = mapper.build_payload(llm_output)

    # 3. プロンプト構築
    payload = scene_json.get("payload", scene_json)
    prompt = build_prompt(payload)

    # 4. 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = os.path.join(OUTPUT_DIR, f"prompt_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(prompt, f, indent=2, ensure_ascii=False)

    return llm_output, scene_json["scene_code"], out_path

# === Gradio UI ===
with gr.Blocks(title="H-K9 思想生成GUI") as demo:
    gr.Markdown("# 🧠 H-K9 思想生成インターフェース")
    with gr.Row():
        user_instruction = gr.Textbox(label="📝 あなたの指示（日本語OK）", lines=4, placeholder="例：濡れた制服の教室構成を作って")
        tags = gr.Textbox(label="🧩 構造タグ（任意・カンマ区切り）", placeholder="A01,C01,D02")

    run_button = gr.Button("🚀 思想を構造に変換して実行準備")
    llm_output = gr.Textbox(label="🧠 LLM出力", lines=6)
    scene_code = gr.Textbox(label="🧬 生成された scene_code")
    output_path = gr.Textbox(label="📁 保存されたプロンプトファイル")

    run_button.click(fn=generate_all, inputs=[user_instruction, tags], outputs=[llm_output, scene_code, output_path])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
