import json
import requests
import os
import sys
from pathlib import Path

# =========================================================
# 🏛️ H-K9 System: Central Command Unit (Main.py)
# =========================================================

# 物理パス設定（genesis_ultimate_final.py の構成に準拠）
BASE_DIR = Path("/workspace/Project-Dystopia-Core")
DICTIONARY_PATH = BASE_DIR / "config/dictionary/h_k9_dictionary_V2_Final.json"
COMFY_URL = "http://127.0.0.1:8888/prompt"

def execute_h_k9_v2(script_id):
    """
    聖典V2から「詳細」と「物理定数」を抽出し、5090へ射出する
    """
    if not DICTIONARY_PATH.exists():
        print(f"❌ [Error] 聖典が見つかりません: {DICTIONARY_PATH}")
        return

    print(f"🐺 [H-K9] 聖典ログ {script_id} をスキャン中...")
    
    with open(DICTIONARY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. 聖典からV2オブジェクトを抽出
    protocol = data.get(script_id)
    if not protocol:
        print(f"⚠️  [Warning] ID: {script_id} は聖典に定義されていません。")
        return

    detail = protocol.get("detail", "")
    physics = protocol.get("physics", "")
    print(f"🧠 [Thought] 翻訳完了: {detail[:50]}...")
    print(f"⚙️  [Physics] 物理演算定数: {physics}")

    # 2. 23,000行の工場（JSONワークフロー）の構築・射出
    # ここではシンプルにプロンプトを ComfyUI API 形式でパッキング
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 42, # 本来はランダム化
                "steps": 35,
                "cfg": 4.5,
                "sampler_name": "dpmpp_2m_sde_gpu",
                "scheduler": "karras",
                "denoise": 0.42, # Z-Image 最適化値
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "zimage_6b.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1536, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": f"{detail}, {physics}, raw photo, high quality"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "illustration, painting, plastic skin, blurry"}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": f"H-K9_{script_id}", "images": ["8", 0]}}
    }

    try:
        res = requests.post(COMFY_URL, json={"prompt": workflow})
        if res.status_code == 200:
            print(f"🔥 [Launch] 5090 Blackwell が現像を開始。Prompt ID: {res.json().get('prompt_id')}")
        else:
            print(f"❌ [Rejected] API Error: {res.text}")
    except Exception as e:
        print(f"❌ [Error] 接続失敗: {e}")

if __name__ == "__main__":
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🐺 H-K9 HEAVY OPERATION CENTER: ACTIVE")
    print("聖典のID（例: V2_執行ログ#151_1）を入力してください。")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    while True:
        cmd = input("H-K9 >> ").strip()
        if cmd.lower() in ['exit', 'quit']:
            break
        if cmd.startswith("V2_"):
            execute_h_k9_v2(cmd)
        else:
            print("💡 'V2_' で始まるIDを入力してください。")
