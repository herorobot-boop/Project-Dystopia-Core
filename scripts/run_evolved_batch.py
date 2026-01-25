import json
import time
import shutil
from pathlib import Path
from prompt_to_comfy import build_comfy_payload
from workflow_mapper import WorkflowMapper
from comfy_client import ComfyClient

# --- パス・設定 ---
BASE_DIR = Path("/workspace/Project-Dystopia")
EVOLVED_DIR = BASE_DIR / "outputs/evolved_thoughts"
DONE_DIR = EVOLVED_DIR / "deployed" # 送信完了した思想の退避先
TEMPLATE_JSON = BASE_DIR / "config/workflow_api_template.json"
OUTPUT_DIR = BASE_DIR / "outputs/payload_logs"

# フォルダの準備
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DONE_DIR.mkdir(parents=True, exist_ok=True)

def run_evolved_batch():
    client = ComfyClient(server_address="127.0.0.1:8188")
    
    if not TEMPLATE_JSON.exists():
        print(f"❌ Error: {TEMPLATE_JSON} が見当たりません。")
        return

    mapper = WorkflowMapper(str(TEMPLATE_JSON))

    # 進化思想ファイルの取得
    evolved_files = sorted(EVOLVED_DIR.glob("evolved_*.json"))
    if not evolved_files:
        print("⚠️ 待機中の進化思想が見つかりません。")
        return

    print(f"🚀 Project Dystopia: {len(evolved_files)}件の進化思想を召喚します。")

    for idx, path in enumerate(evolved_files):
        print(f"\n🧬 [{idx+1}/{len(evolved_files)}] 進化個体を転送中: {path.name}")
        
        with open(path, "r", encoding="utf-8") as f:
            thought = json.load(f)

        # ペイロード構築とマッピング
        payload = build_comfy_payload(thought)
        final_workflow = mapper.inject_payload(payload)
        
        # ComfyUI API送信
        response = client.queue_prompt(final_workflow)

        if response:
            prompt_id = response.get("prompt_id")
            print(f"📡 受理完了。Prompt ID: {prompt_id}")
            
            # ログの記録
            log_data = {"thought": thought, "params": payload["params"], "prompt_id": prompt_id}
            with open(OUTPUT_DIR / f"{prompt_id}.json", "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            # 送信済みファイルを移動（二重送信防止）
            shutil.move(str(path), str(DONE_DIR / path.name))
        else:
            print(f"⚠️ {path.name} の送信に失敗しました。")

        time.sleep(2) # ネットワークとAPIの安定のため

    print("\n🌿 全進化思想のデプロイが完了しました。画像が生成されるのを待機してください。")

if __name__ == "__main__":
    run_evolved_batch()
