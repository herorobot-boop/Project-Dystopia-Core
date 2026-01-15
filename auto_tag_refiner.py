import os

def refine_caption(text):
    # ルールベース補正（例：不要語削除、構造語追加）
    text = text.lower()
    text = text.replace("a ", "").replace("the ", "")
    text = text.replace("blurry", "")
    if "microphone" in text:
        text += ", type_e, concept_biomic"
    if "fluid" in text or "wet" in text:
        text += ", type_c, fluid_resource"
    return text.strip()

def refine_folder(folder):
    for fname in os.listdir(folder):
        if fname.endswith(".txt"):
            path = os.path.join(folder, fname)
            with open(path, "r") as f:
                raw = f.read()
            refined = refine_caption(raw)
            with open(path, "w") as f:
                f.write(refined)
            print(f"🧠 {fname} → 補正完了")
