from PIL import Image
import numpy as np
import os

def detect_breakdown(image_path, threshold=30):
    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.float32)
    laplacian = np.abs(np.gradient(arr)[0]) + np.abs(np.gradient(arr)[1])
    sharpness = laplacian.var()
    return sharpness < threshold  # true = 破綻とみなす

def scan_folder_for_breakdown(folder):
    breakdowns = []
    for fname in os.listdir(folder):
        if fname.endswith(".png"):
            path = os.path.join(folder, fname)
            if detect_breakdown(path):
                breakdowns.append(fname)
    return breakdowns
