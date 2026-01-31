# [GitHub] Project-Dystopia-Nodes / camera_bridge.py
# Purpose: Bridge QwenMultiAngle and Wan 2.6 Camera Control

class DystopiaCameraBridge:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "angle_dict": ("DICT",),
                "camera_move": (["Zoom In", "Pan Left", "Orbit"],),
            }
        }

    RETURN_TYPES = ("PROMPT_STR",)
    FUNCTION = "process"
    CATEGORY = "Dystopia"

    def process(self, angle_dict, camera_move):
        # 3Dアングル値を動画モデルのテキストプロンプトへ変換
        return (f"Camera {camera_move}, yaw {angle_dict.get('yaw', 0)}",)

NODE_CLASS_MAPPINGS = {"DystopiaCameraBridge": DystopiaCameraBridge}
