from PIL import Image
import numpy as np
import os

def estimate_blur(image_path):
    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.float32)
    laplacian = np.abs(np.gradient(arr)[0]) + np.abs(np.gradient(arr)[1])
    score = laplacian.var()
    return round(score, 2)

def suggest_score(image_folder):
    scores = []
    for fname in os.listdir(image_folder):
        if fname.endswith(".png") or fname.endswith(".jpg"):
            path = os.path.join(image_folder, fname)
            blur = estimate_blur(path)
            scores.append(blur)

    avg = np.mean(scores)
    print(f"📊 平均シャープネススコア: {round(avg, 2)}")

    if avg < 50:
        print("⚠️ 破綻率高：LoRA強度が高すぎる可能性あり")
    elif avg < 150:
        print("✅ 安定：構造・質感がバランス良好")
    else:
        print("🧪 高精細：強度制御性が高い可能性あり")
