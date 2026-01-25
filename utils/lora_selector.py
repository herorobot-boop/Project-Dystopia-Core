import pandas as pd
import random
import os
from pathlib import Path

# --- 神経接続：プロジェクトルートの特定 ---
BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "config/assets"

def get_asset_path():
    """整理されたフォルダ内からCSV資産ファイルを特定する"""
    # 特定のファイル名に依存せず、config/assets 内の .csv を探す
    csv_files = list(ASSETS_DIR.glob("*.csv"))
    if not csv_files:
        # フォールバック：整理時に移動させた名前を優先
        backup_path = ASSETS_DIR / "Gdrive_Asset_List_v2-10.xlsx - シート1.csv"
        return backup_path
    
    # 複数のCSVがある場合は、最新または最もそれらしいものを選択（ここでは最初の1つ）
    return csv_files[0]

def get_available_loras():
    """CSVからLoRAファイル名のリストを動的に取得する"""
    path = get_asset_path()
    if not path.exists():
        print(f"[-] Warning: Asset CSV not found at {path}")
        return []

    try:
        # 読み込みエラー回避のため encoding を指定
        df = pd.read_csv(path, encoding='utf-8')
        # 'File Name' カラムから .safetensors を抽出
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
    所持しているLoRA資産と照らし合わせ、シーンに最適なものを召喚する。
    [HERO's Logic Preserved: キーワードマッチングと強制演出ロジックを維持]
    """
    all_assets = get_available_loras()
    if not all_assets:
        return []

    selected = []

    # --- 1. 資産ベースのキーワードマッチング ---
    keywords = scene_context.split() + [view, context_type]
    for asset in all_assets:
        for kw in keywords:
            if kw and kw.lower() in asset.lower():
                selected.append({"name": asset, "weight": round(random.uniform(0.5, 0.8), 2)})
                break
    
    # --- 2. 必須演出LoRAの強制適用（HERO's Specialized Logic） ---
    # POV演出 (paid文脈)
    if context_type == "paid" and any("Pov_xl" in a for a in all_assets):
        target = next((a for a in all_assets if "Pov_xl" in a), "Pov_xl_v1.5")
        selected.append({"name": target, "weight": 0.4})

    # 公衆電話演出
    if "電話" in scene_context and any("Public_Phone" in a for a in all_assets):
        target = next((a for a in all_assets if "Public_Phone" in a), "Japanese_Public_Phone_SDXL")
        selected.append({"name": target, "weight": 0.7})

    # --- 3. 重複削除と制限 ---
    unique_selected = {l['name']: l for l in selected}.values()
    return list(unique_selected)[:3]

if __name__ == "__main__":
    # テスト：新構造での資産検知
    print(f"[*] Assets Directory: {ASSETS_DIR}")
    loras = select_lora("雨の公衆電話で誰かを待つ", "Eye_Level", "paid")
    print("\n🔮 Selected LoRAs for Scene:")
    print(loras)
