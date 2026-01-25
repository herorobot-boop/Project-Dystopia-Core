import pandas as pd
import random
import os
from pathlib import Path

# --- 神経接続：プロジェクトルートの特定 ---
BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "config/assets"

def get_asset_path():
    """整理されたフォルダ内からCSV資産ファイルを特定する"""
    csv_files = list(ASSETS_DIR.glob("*.csv"))
    if not csv_files:
        backup_path = ASSETS_DIR / "Gdrive_Asset_List_v2-10.xlsx - シート1.csv"
        return backup_path
    return csv_files[0]

def get_available_loras():
    """CSVからLoRAファイル名のリストを動的に取得する"""
    path = get_asset_path()
    if not path.exists():
        print(f"[-] Warning: Asset CSV not found at {path}")
        return []

    try:
        df = pd.read_csv(path, encoding='utf-8')
        if 'File Name' not in df.columns:
            print(f"[-] Error: 'File Name' column missing in {path.name}")
            return []
            
        lora_list = df[df['File Name'].str.endswith('.safetensors', na=False)]['File Name'].tolist()
        return [n.replace('.safetensors', '') for n in lora_list]
    except Exception as e:
        print(f"[-] Error loading CSV ({path.name}): {e}")
        return []

def select_lora(scene_context: str, view: str = "", context_type: str = "free") -> list:
    """
    [H-K9 Optimized: context_typeに応じた動的強度(Weight)の割り振り]
    """
    all_assets = get_available_loras()
    if not all_assets:
        return []

    selected = []
    
    # --- 1. context_typeによる強度基準の策定 ---
    # paid: 物理変形を限界まで強調 / free: 自然なリアリズム
    if context_type == "paid":
        base_min, base_max = 0.8, 1.0  # 強力な物理干渉
    elif context_type == "teaser":
        base_min, base_max = 0.6, 0.8  # 期待感を煽る質感
    else:
        base_min, base_max = 0.4, 0.6  # 安定した日常感

    # --- 2. 資産ベースのキーワードマッチング ---
    keywords = scene_context.split() + [view, context_type]
    for asset in all_assets:
        for kw in keywords:
            if kw and kw.lower() in asset.lower():
                weight = round(random.uniform(base_min, base_max), 2)
                selected.append({"name": asset, "weight": weight})
                break
    
    # --- 3. 必須演出LoRAの強制適用（物理特化ブースト） ---
    # POV演出 (paid文脈)
    if context_type == "paid" and any("Pov_xl" in a for a in all_assets):
        target = next((a for a in all_assets if "Pov_xl" in a), "Pov_xl_v1.5")
        selected.append({"name": target, "weight": 0.6}) # POVの深度を強化

    # 公衆電話演出
    if "電話" in scene_context and any("Public_Phone" in a for a in all_assets):
        target = next((a for a in all_assets if "Public_Phone" in a), "Japanese_Public_Phone_SDXL")
        selected.append({"name": target, "weight": 0.85})

    # --- 4. 重複削除と制限 ---
    unique_selected = {l['name']: l for l in selected}.values()
    return list(unique_selected)[:3]

if __name__ == "__main__":
    print(f"[*] Assets Directory: {ASSETS_DIR}")
    # 有料個体のシミュレーション
    loras = select_lora("深夜の密室内、資源が堆積する", "Extreme_Close_Up", "paid")
    print("\n🔮 High-Intensity LoRAs for Paid Scene:")
    print(loras)
