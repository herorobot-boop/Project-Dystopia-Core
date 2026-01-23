import json
import requests
from pathlib import Path
from datetime import datetime

# --- パス設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
WORKFLOW_PATH = BASE_PATH / "workflows/Type-V_Video_Template.json"
EVOLVED_THOUGHTS_DIR = BASE_PATH / "outputs/evolved_thoughts"
PAYLOAD_LOG_DIR = BASE_PATH / "outputs/payload_logs"

COMFY_URL = "http://127.0.0.1:8188/prompt"

def load_latest_evolved_thoughts():
    """最新の進化済み思想ファイルを読み込む"""
    files = sorted(EVOLVED_THOUGHTS_DIR.glob("evolved_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not files:
        print("⚠️ 進化済み思想が見つかりません。")
        return []
    with open(files[0], "r", encoding="utf-8") as f:
        return json.load(f)

def queue_video_job(payload, prompt_id):
    """ComfyUI APIへジョブを送信"""
    try:
        response = requests.post(COMFY_URL, json={"prompt": payload})
        if response.status_code == 200:
            print(f"🎬 Video Job Queued: {prompt_id}")
            return response.json().get("prompt_id", "unknown")
        else:
            print(f"❌ APIエラー: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"📡 接続エラー: {e}")
    return None

def build_video_payload(thought, workflow_template):
    """動画用ペイロードの構築"""
    prompt_id = thought.get("prompt_id", f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    scene = thought.get("scene", "a cinematic scene")

    wf = json.loads(json.dumps(workflow_template))  # 深いコピー

    # ノードIDはテンプレートに合わせて調整
    if "6" in wf:
        wf["6"]["inputs"]["text"] = f"{scene}, cinematic motion, high quality"
    if "10" in wf and "lora_name" in thought:
        wf["10"]["inputs"]["lora_name"] = thought["lora_name"]

    return wf, prompt_id

def main():
    if not WORKFLOW_PATH.exists():
        print(f"⚠️ 動画用ワークフローが見つかりません: {WORKFLOW_PATH}")
        return

    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        template = json.load(f)

    thoughts = load_latest_evolved_thoughts()
    if not thoughts:
        print("⚠️ 送信する思想がありません。先に evaluator.py を実行してください。")
        return

    PAYLOAD_LOG_DIR.mkdir(exist_ok=True)
    print(f"🚀 {len(thoughts)} 件の動画生成ジョブを送信します...")

    for t in thoughts:
        payload, p_id = build_video_payload(t, template)

        # ログ保存
        log_file = PAYLOAD_LOG_DIR / f"video_payload_{p_id}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        queue_video_job(payload, p_id)

if __name__ == "__main__":
    main()
