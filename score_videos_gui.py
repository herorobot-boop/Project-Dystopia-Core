import gradio as gr
import json
from pathlib import Path
from datetime import datetime

# --- パス設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
VIDEO_DIR = BASE_PATH / "outputs/videos"
LOG_PATH = BASE_PATH / "outputs/video_thought_log.jsonl"

def load_existing_log():
    """既存の評価ログを読み込む"""
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def get_unscored_videos():
    """未評価の動画ファイルをリストアップ"""
    if not VIDEO_DIR.exists():
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        return []
    
    existing_ids = {entry["prompt_id"] for entry in load_existing_log()}
    # .mp4ファイルをすべて取得し、未評価のものだけ残す
    all_videos = sorted(VIDEO_DIR.glob("*.mp4"), key=lambda x: x.stat().st_mtime)
    return [v for v in all_videos if v.stem not in existing_ids]

def save_score(prompt_id, scene, lora, score, meta):
    """評価結果をJSONL形式で追記保存"""
    entry = {
        "prompt_id": prompt_id,
        "scene": scene,
        "lora": lora,
        "score": float(score),
        "timestamp": datetime.now().isoformat(),
        "meta": meta
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# --- UI制御ロジック ---
def load_next():
    unscored = get_unscored_videos()
    
    if not unscored:
        return None, "🎉 全動画の評価完了、または動画がありません", "", "", "{}", 5.0

    # 最初の未評価動画を選択
    video_path = unscored[0]
    prompt_id = video_path.stem

    # 同名のJSONファイルからメタデータを探索
    meta_path = VIDEO_DIR / f"{prompt_id}.json"
    meta_data = {}
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Meta read error: {e}")

    scene = meta_data.get("scene", "N/A (No scene data found)")
    lora = meta_data.get("lora_name", meta_data.get("lora", "N/A"))
    
    meta_info = {
        "frames": meta_data.get("frames", 16),
        "fps": meta_data.get("fps", 8),
        "generation": meta_data.get("generation", 1),
        "ancestor": meta_data.get("ancestor", None)
    }

    return str(video_path), prompt_id, scene, lora, json.dumps(meta_info, ensure_ascii=False, indent=2), 5.0

def submit_score(prompt_id, scene, lora, meta_json, score):
    if prompt_id and "評価完了" not in prompt_id:
        try:
            meta = json.loads(meta_json)
            save_score(prompt_id, scene, lora, score, meta)
        except Exception as e:
            print(f"❌ Save Error: {e}")
    return load_next()

# --- Gradio UI 構成 ---
with gr.Blocks(title="Project Dystopia: Motion Evaluator") as demo:
    gr.Markdown("# 🎞️ Project Dystopia: 動画評価フェーズ")
    gr.Markdown("生成された『動く思想』に判決を下してください。")

    with gr.Row():
        with gr.Column(scale=2):
            video_player = gr.Video(label="Reviewing Motion")
        with gr.Column(scale=1):
            prompt_id_box = gr.Textbox(label="Prompt ID", interactive=False)
            scene_box = gr.TextArea(label="Scene Description", interactive=False)
            lora_box = gr.Textbox(label="Applied LoRA", interactive=False)
            meta_box = gr.Code(label="Meta Info", language="json", interactive=False)
            
            score_slider = gr.Slider(1, 10, value=5.0, step=0.5, label="審美スコア")
            
            with gr.Row():
                submit_btn = gr.Button("判決を確定 (Submit)", variant="primary")
                skip_btn = gr.Button("保留 (Skip)")

    # イベントハンドラ
    submit_btn.click(
        submit_score,
        inputs=[prompt_id_box, scene_box, lora_box, meta_box, score_slider],
        outputs=[video_player, prompt_id_box, scene_box, lora_box, meta_box, score_slider]
    )
    skip_btn.click(
        load_next,
        outputs=[video_player, prompt_id_box, scene_box, lora_box, meta_box, score_slider]
    )
    
    # 初期ロード
    demo.load(load_next, outputs=[video_player, prompt_id_box, scene_box, lora_box, meta_box, score_slider])

if __name__ == "__main__":
    # RunPod 外部アクセス用
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
