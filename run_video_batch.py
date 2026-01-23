import json
import requests
import random
from pathlib import Path
from datetime import datetime

# --- パス設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
WORKFLOW_PATH = BASE_PATH / "workflows/Type-V_Video_Template.json"
# 進化済み動画思想のディレクトリ
EVOLVED_DIR = BASE_PATH / "outputs/evolved_thoughts"
PAYLOAD_LOG_DIR = BASE_PATH / "outputs/payload_logs"

COMFY_URL = "http://127.0.0.1:8188/prompt"

def get_latest_evolved_file():
    """最新の evolved_video_*.json を取得"""
    files = sorted(EVOLVED_DIR.glob("evolved_video_*.json"), reverse=True)
    return files[0] if files else None

def queue_video_job(payload, prompt_id):
    try:
        response = requests.post(COMFY_URL, json={"prompt": payload})
        if response.status_code == 200:
            print(f"🎬 Queued: {prompt_id}")
            return response.json().get("prompt_id")
        else:
            print(f"❌ API Error: {response.text}")
    except Exception as e:
        print(f"📡 Connection Error: {e}")
    return None

def build_video_payload(thought, template):
    """進化思想（frames, fps等）をワークフローに反映"""
    wf = json.loads(json.dumps(template))
    p_id = thought["prompt_id"]
    scene = thought["scene"]
    meta = thought.get("meta", {})

    # ID "2": Prompt (sceneの注入)
    if "2" in wf:
        wf["2"]["inputs"]["text"] = f"{scene}, cinematic motion, high quality"

    # ID "1": EmptyLatentImage (framesの注入)
    if "1" in wf:
        wf["1"]["inputs"]["frames"] = meta.get("frames", 16)

    # ID "7": SaveVideo (fpsの注入)
    if "7" in wf:
        wf["7"]["inputs"]["fps"] = meta.get("fps", 8)

    # ID "5": KSampler (Seedのランダム化)
    if "5" in wf:
        wf["5"]["inputs"]["seed"] = random.randint(0, 0xffffffffffffffff)

    return wf, p_id

def main():
    if not WORKFLOW_PATH.exists():
        print("⚠️ テンプレートが見つかりません。")
        return

    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        template = json.load(f)

    # 進化済み思想の読み込み
    evolved_file = get_latest_evolved_file()
    if not evolved_file:
        print("⚠️ 進化済み思想ファイルが存在しません。evolve_video_batch.pyを先に実行してください。")
        return

    with open(evolved_file, "r", encoding="utf-8") as f:
        thoughts = json.load(f)

    PAYLOAD_LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"🚀 Processing {len(thoughts)} thoughts from {evolved_file.name}")

    for t in thoughts:
        payload, p_id = build_video_payload(t, template)
        
        # 検証用ログ
        with open(PAYLOAD_LOG_DIR / f"video_{p_id}.json", "w") as f:
            json.dump(payload, f, indent=2)

        queue_video_job(payload, p_id)

if __name__ == "__main__":
    main()
