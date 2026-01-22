import pandas as pd
import random
from pathlib import Path

# CSVのパス（アップロードされたファイル名に合わせて調整）
ASSET_LIST_PATH = Path("/workspace/Project-Dystopia/config/Gdrive_Asset_List_v2-10.xlsx - シート1.csv")

def get_available_loras():
    """CSVからLoRAファイル名のリストを動的に取得する"""
    try:
        df = pd.read_csv(ASSET_LIST_PATH)
        # .safetensorsで終わるファイル名のみを抽出
        lora_list = df[df['File Name'].str.endswith('.safetensors', na=False)]['File Name'].tolist()
        # 拡張子を除いた名前をキーにする
        return [n.replace('.safetensors', '') for n in lora_list]
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []

def select_lora(scene_context: str, view: str = "", context_type: str = "free") -> list:
    """
    所持しているLoRA資産と照らし合わせ、シーンに最適なものを召喚する。
    """
    all_assets = get_available_loras()
    selected = []

    # --- 1. 資産ベースのキーワードマッチング ---
    # シーンや構図に関連するLoRAが資産リストにあれば優先採用
    keywords = scene_context.split() + [view, context_type]
    for asset in all_assets:
        for kw in keywords:
            if kw.lower() in asset.lower():
                # 重みをランダムに設定して採用
                selected.append({"name": asset, "weight": round(random.uniform(0.5, 0.8), 2)})
                break
    
    # --- 2. 必須演出LoRAの強制適用（資産にあれば） ---
    # POV演出 (paid文脈)
    if context_type == "paid" and "Pov_xl_v1.5" in all_assets:
        selected.append({"name": "Pov_xl_v1.5", "weight": 0.4})

    # 公衆電話演出
    if "電話" in scene_context and "Japanese_Public_Phone_SDXL" in all_assets:
        selected.append({"name": "Japanese_Public_Phone_SDXL", "weight": 0.7})

    # --- 3. 重複削除と制限 ---
    # LoRAが多すぎると崩れるため、最大3つまでに絞る
    unique_selected = {l['name']: l for l in selected}.values()
    return list(unique_selected)[:3]
