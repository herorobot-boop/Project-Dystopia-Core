import json
import time
import requests
import random
from pathlib import Path
from thought_generator import generate_thought
from prompt_to_comfy import build_comfy_payload

# --- 設定 ---
COMFY_API_URL = "http://127.0.0.1:8188/prompt"
BASE_DIR = Path("/workspace/Project-Dystopia")
OUTPUT_DIR = BASE_DIR / "outputs/payload_logs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- バッチ対象のシーンリスト ---
SCENE_LIST = [
    "雨の公衆電話で誰かを待つ",
    "深夜のコンビニ、駐車場、防犯カメラの視点",
    "放課後の教室、夕日が差し込む",
    "駅のホーム、傘を持った女子高生",
    "古びた体育館、床に反射する光"
]

def send_to_comfy(payload: dict):
    """
    ComfyUIのAPIにペイロードを送信する。
    ※ComfyUI APIは {"prompt": workflow_json} の形式を期待するため、
    実際の実装ではここでワークフローJSONとマージする必要があります。
    """
    # 簡易版：現在はペイロードの確認まで。
    # ワークフローJSONとの合体ロジックが完成したらここを有効化。
    try:
        # 構造をComfyUI APIの期待する形式に調整
        # 本来はここで ComfyUI の API JSON ノードとマッピングします
        response = requests.post(COMFY_API_URL, json={"prompt": payload, "client_id": "dystopia_bot"})
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

def run_batch(context_type="teaser", width=832, height=1216, model="SDXL"):
    print(f"🚀 Project Dystopia: Starting Batch Generation [{context_type.upper()}]")
    
    for idx, scene in enumerate(SCENE_LIST):
        print(f"\n🌀 [{idx+1}/{len(SCENE_LIST)}] Processing: {scene}")
        
        # 1. 思想の生成（魂の構築）
        thought = generate_thought(scene_context=scene, context_type=context_type, variation_id=idx)
        
        # 2. ペイロード化（肉体の構築）
        # シード値をここで固定してログに残す
        current_seed = random.randint(0, 10**16)
        payload = build_comfy_payload(thought, width=width, height=height, seed=current_seed, model=model)

        # 3. 思想ログの保存（進化の種）
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        out_path = OUTPUT_DIR / f"{timestamp}_{idx}_{context_type}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Payload Saved: {out_path.name} (Seed: {current_seed})")

        # 4. ComfyUIへの送信
        # ※API用ワークフローJSONが未配備の場合は、ドライラン（保存のみ）として機能
        status, result = send_to_comfy(payload)
        
        if status == 200:
            print(f"📡 Sent to ComfyUI successfully.")
        else:
            print(f"⚠️ Sent bypass (or error): {status} - API workflow template might be needed.")

        time.sleep(1.0) # 連続送信による負荷軽減

    print("\n✅ Batch process completed.")

if __name__ == "__main__":
    # 実弾射撃（有料会員向けクオリティで一括生成）
    run_batch(context_type="paid")
