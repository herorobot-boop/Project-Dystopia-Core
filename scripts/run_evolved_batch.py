import json
import time
import shutil
import sys
from pathlib import Path

# --- パス解決とインポート ---
BASE_DIR = Path(__file__).resolve().parents[1]
for folder in ["core/engines", "utils"]:
    sys.path.append(str(BASE_DIR / folder))

from prompt_to_comfy import build_comfy_payload
from workflow_mapper import WorkflowMapper
try:
    from comfy_client import ComfyClient
except ImportError:
    class ComfyClient: # フォールバック
        def __init__(self, **kwargs): pass
        def queue_prompt(self, p): return {"prompt_id": "test_id"}

# --- フォルダ設定 ---
EVOLVED_DIR = BASE_DIR / "outputs/manuals/evolved_thoughts"
DONE_DIR = EVOLVED_DIR / "deployed"
TEMPLATE_JSON = BASE_DIR / "workflows/Chronos_V3_Workflow.json"
OUTPUT_LOG_DIR = BASE_DIR / "outputs/payload_logs"

def run_evolved_batch():
    """
    進化個体（JSON）を順次 ComfyUI へ送信し、完了後に退避させる。
    """
    EVOLVED_DIR.mkdir(parents=True, exist_ok=True)
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    
    client = ComfyClient(server_address="127.0.0.1:8188")
    mapper = WorkflowMapper(template_name=TEMPLATE_JSON.name)

    evolved_files = sorted(EVOLVED_DIR.glob("evolved_*.json"))
    if not evolved_files:
        print("⚠️ 待機中の進化個体が見つかりません。")
        return

    print(f"🚀 Project Dystopia: {len(evolved_files)}件の進化思想を召喚します。")

    for path in evolved_files:
        print(f"\n🧬 進化個体転送中: {path.name}")
        
        with open(path, "r", encoding="utf-8") as f:
            thought = json.load(f)

        payload = build_comfy_payload(thought)
        final_workflow = mapper.inject_payload(payload)
        response = client.queue_prompt(final_workflow)

        if response:
            prompt_id = response.get("prompt_id")
            print(f"📡 受理完了 ID: {prompt_id}")
            
            # ログ記録
            with open(OUTPUT_LOG_DIR / f"{prompt_id}.json", "w", encoding="utf-8") as f:
                json.dump({"thought": thought, "prompt_id": prompt_id}, f, indent=2, ensure_ascii=False)
            
            # 二重送信防止の退避
            shutil.move(str(path), str(DONE_DIR / path.name))
        
        time.sleep(2)

if __name__ == "__main__":
    run_evolved_batch()
