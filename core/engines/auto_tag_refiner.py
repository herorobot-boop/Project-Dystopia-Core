import os
from pathlib import Path

def refine_caption(text):
    """
    [HERO's Logic Preserved: 不要語削除と概念タグ（type_e, type_c等）の自動付与]
    """
    text = text.lower()
    # 冗長な表現の排除
    text = text.replace("a ", "").replace("the ", "").replace("blurry", "")
    
    # H-K9 独自概念の注入
    if "microphone" in text:
        text += ", type_e, concept_biomic"
    if "fluid" in text or "wet" in text:
        text += ", type_c, fluid_resource"
    
    return text.strip().strip(",")

def refine_folder(folder_path):
    """
    指定フォルダ内の全ての .txt キャプションを一括補正する
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"[-] Directory not found: {folder}")
        return

    for txt_file in folder.glob("*.txt"):
        try:
            raw = txt_file.read_text(encoding="utf-8")
            refined = refine_caption(raw)
            txt_file.write_text(refined, encoding="utf-8")
            print(f"🧠 {txt_file.name} → 補正完了")
        except Exception as e:
            print(f"[-] Error refining {txt_file.name}: {e}")
