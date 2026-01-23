import gradio as gr
import json
from pathlib import Path
from PIL import Image

# --- パス設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
LOG_PATH = BASE_PATH / "outputs/thought_log.jsonl"
IMAGE_DIR = BASE_PATH / "outputs/images"

def get_unscored_data():
    """未評価の思想を抽出"""
    if not LOG_PATH.exists():
        return []
    data = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue
    return [d for d in data if d.get("score") is None]

def save_score(prompt_id, score):
    """スコアをログファイルに永続化"""
    all_data = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                all_data.append(json.loads(line))
            except:
                continue

    for d in all_data:
        if d.get("prompt_id") == prompt_id:
            d["score"] = float(score)
            break

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for d in all_data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

# --- UI Logic ---
unscored_list = get_unscored_data()
current_index = 0

def load_next():
    global current_index, unscored_list
    unscored_list = get_unscored_data()
    if current_index >= len(unscored_list):
        return None, "🎉 すべての評価が完了しました！", "", ""

    item = unscored_list[current_index]
    img_path = IMAGE_DIR / f"{item['prompt_id']}.png"
    if not img_path.exists():
        return None, f"⚠️ 画像が見つかりません: {img_path.name}", item['scene'], item['prompt_id']

    info_text = f"🧬 Gen: {item['meta'].get('generation', 0)} | Context: {item.get('context')}"
    return str(img_path), info_text, item['scene'], item['prompt_id']

def submit(prompt_id, score):
    global current_index
    if prompt_id:
        save_score(prompt_id, score)
        current_index += 1
    return load_next()

# --- Gradio UI ---
with gr.Blocks(title="Project Dystopia Evaluator") as demo:
    gr.Markdown("# 👁️ Project Dystopia: 審美眼の法廷")

    with gr.Row():
        with gr.Column(scale=2):
            main_img = gr.Image(label="Generated Image", type="filepath")
        with gr.Column(scale=1):
            with gr.Group():
                id_display = gr.Textbox(label="Prompt ID", interactive=False)
                info_display = gr.Text(label="Meta Info", interactive=False)
                scene_display = gr.TextArea(label="Scene Thought", interactive=False)

            score_slider = gr.Slider(1, 10, value=5, step=0.5, label="審美スコア")
            submit_btn = gr.Button("判決を下す (Submit)", variant="primary")
            skip_btn = gr.Button("保留 (Skip)")

    submit_btn.click(submit, inputs=[id_display, score_slider],
                     outputs=[main_img, info_display, scene_display, id_display])
    skip_btn.click(load_next,
                   outputs=[main_img, info_display, scene_display, id_display])
    demo.load(load_next, outputs=[main_img, info_display, scene_display, id_display])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
