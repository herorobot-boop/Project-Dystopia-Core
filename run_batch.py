import json
import time
from pathlib import Path
from thought_generator import generate_thought
from prompt_to_comfy import build_comfy_payload
from workflow_mapper import WorkflowMapper
from comfy_client import ComfyClient

# --- パス・設定 ---
BASE_DIR = Path("/workspace/Project-Dystopia")
TEMPLATE_JSON = BASE_DIR / "config/workflow_api_template.json"
OUTPUT_DIR = BASE_DIR / "outputs/payload_logs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCENE_LIST = [
    "雨の公衆電話で誰かを待つ",
    "深夜のコンビニ、駐車場、防犯カメラの視点",
    "放課後の教室、夕日が差し込む"
]

def run_batch(context_type="paid"):
    # 1. 準備：クライアントとマッパーの起動
    client = ComfyClient(server_address="127.0.0.1:8188")
    
    if not TEMPLATE_JSON.exists():
        print(f"❌ Error: {TEMPLATE_JSON} が見当たりません。ComfyUIからAPI用JSONを書き出してください。")
        return

    mapper = WorkflowMapper(str(TEMPLATE_JSON))

    for idx, scene in enumerate(SCENE_LIST):
        print(f"\n🌀 [{idx+1}/{len(SCENE_LIST)}] 思想展開中: {scene}")
        
        # 2. 思想生成 & ペイロード構築
        thought = generate_thought(scene, context_type=context_type)
        payload = build_comfy_payload(thought)

        # 3. ワークフローへのマッピング（精密合成）
        final_workflow = mapper.inject_payload(payload)

        # 4. ComfyUIへ送信（神経伝達）
        response = client.queue_prompt(final_workflow)
        
        if response:
            prompt_id = response.get("prompt_id")
            print(f"📡 ComfyUIが受理しました。Prompt ID: {prompt_id}")
            
            # ログ保存
            log_data = {"thought": thought, "prompt_id": prompt_id}
            with open(OUTPUT_DIR / f"{prompt_id}.json", "w") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        time.sleep(2) # キューの詰まり防止

    print("\n✅ 全思想の送信が完了しました。")

if __name__ == "__main__":
    run_batch()
