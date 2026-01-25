import json
import time
import sys
from pathlib import Path

# --- 神経接続：プロジェクトルートとモジュールパスの特定 ---
BASE_DIR = Path(__file__).resolve().parents[1]

# 依存フォルダ（core/engines と utils）を検索パスに追加
for folder in ["core/engines", "utils"]:
    module_path = BASE_DIR / folder
    if str(module_path) not in sys.path:
        sys.path.append(str(module_path))

# --- エンジン・ユーティリティのインポート ---
try:
    from thought_generator import generate_thought
    from prompt_to_comfy import build_comfy_payload
    from workflow_mapper import WorkflowMapper
    # ComfyClient が utils または core/engines にある前提
    # なければ最低限の代替クラスを用意するか、適宜インポート先を調整
    try:
        from comfy_client import ComfyClient
    except ImportError:
        print("[-] Warning: comfy_client.py not found. Using dummy client for test.")
        class ComfyClient:
            def __init__(self, **kwargs): pass
            def queue_prompt(self, p): return {"prompt_id": f"dummy_{int(time.time())}"}
except ImportError as e:
    print(f"[-] Critical Import Error: {e}")
    sys.exit(1)

# --- 設定：新構造への適合 ---
TEMPLATE_JSON = BASE_DIR / "workflows/Chronos_V3_Workflow.json" # 標準テンプレートに固定
OUTPUT_LOG_DIR = BASE_DIR / "outputs/payload_logs"
OUTPUT_LOG_DIR.mkdir(parents=True, exist_ok=True)

SCENE_LIST = [
    "雨の公衆電話で誰かを待つ",
    "深夜のコンビニ、駐車場、防犯カメラの視点",
    "放課後の教室、夕日が差し込む"
]

def run_batch(context_type="paid"):
    """
    複数シーンの一斉執行。
    [HERO's Execution Logic Preserved: 思想生成->マッピング->送信の流れを維持]
    """
    # 1. 準備：クライアントとマッパーの起動
    client = ComfyClient(server_address="127.0.0.1:8188")
    
    if not TEMPLATE_JSON.exists():
        print(f"❌ Error: {TEMPLATE_JSON} が見当たりません。workflows/ フォルダを確認してください。")
        return

    # WorkflowMapper は内部でパス解決済み
    mapper = WorkflowMapper(template_name=TEMPLATE_JSON.name)

    for idx, scene in enumerate(SCENE_LIST):
        print(f"\n🌀 [{idx+1}/{len(SCENE_LIST)}] 思想展開中: {scene}")
        
        # 2. 思想生成 & ペイロード構築
        thought = generate_thought(scene, context_type=context_type)
        payload = build_comfy_payload(thought)

        # 3. ワークフローへのマッピング
        final_workflow = mapper.inject_payload(payload)

        # 4. ComfyUIへ送信
        response = client.queue_prompt(final_workflow)
        
        if response:
            prompt_id = response.get("prompt_id")
            print(f"📡 ComfyUIが受理しました。Prompt ID: {prompt_id}")
            
            # ログ保存（outputs/payload_logs/ へ）
            log_data = {"thought": thought, "prompt_id": prompt_id}
            log_file = OUTPUT_LOG_DIR / f"{prompt_id}.json"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            print(f"📝 ログを記録: {log_file.name}")
        
        time.sleep(2) # キューの詰まり防止

    print("\n✅ 全思想の送信が完了しました。")

if __name__ == "__main__":
    print(f"[*] H-K9 Batch Controller Starting...")
    print(f"[*] Project Root: {BASE_DIR}")
    run_batch()
