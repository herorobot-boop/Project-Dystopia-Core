import random

# LoRA候補リスト（今後はJSONや外部ファイルから読み込む設計に拡張可能）
LORA_POOL = {
    "view_based": {
        "close-up": [
            {"name": "Face_Detail_Enhancer", "weight": 0.8},
            {"name": "Eye_Contact_Boost", "weight": 0.75}
        ],
        "wide": [
            {"name": "Background_Depth_Boost", "weight": 0.6},
            {"name": "Environmental_Lighting", "weight": 0.65}
        ],
        "floor": [
            {"name": "Low_Angle_Drama", "weight": 0.7}
        ]
    },
    "scene_based": {
        "コンビニ": [
            {"name": "Japanese_Convenience_Store", "weight": 0.7}
        ],
        "駅": [
            {"name": "Japanese_Public_Phone_SDXL", "weight": 0.65}
        ],
        "体育館": [
            {"name": "Wooden_Floor_Reflection", "weight": 0.6}
        ]
    },
    "universal": [
        {"name": "Pov_xl_v1.5", "weight": 0.5},
        {"name": "UGC_Noise_Overlay", "weight": 0.55}
    ]
}

def select_lora(scene_context: str, view: str = "", context_type: str = "free") -> list:
    """
    シーンや構図に応じて最適なLoRAを選定する。
    """
    selected = []

    # --- 1. ViewベースのLoRA ---
    view_key = ""
    if "close" in view or "extreme" in view:
        view_key = "close-up"
    elif "wide" in view:
        view_key = "wide"
    elif "floor" in view or "low" in view:
        view_key = "floor"

    if view_key in LORA_POOL["view_based"]:
        selected += random.sample(LORA_POOL["view_based"][view_key], k=1)

    # --- 2. SceneベースのLoRA ---
    for keyword, loras in LORA_POOL["scene_based"].items():
        if keyword in scene_context:
            selected += random.sample(loras, k=1)

    # --- 3. Universal LoRA（文脈に応じて追加） ---
    if context_type == "paid":
        selected += random.sample(LORA_POOL["universal"], k=1)

    return selected
