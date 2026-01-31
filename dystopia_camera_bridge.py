# ---------------------------------------------------------
# Dystopia Camera Bridge v1.0
# QwenMultiAngle の出力を Wan 2.6 (Fun Control) の
# カメラパラメータへ自動変換するノード
# ---------------------------------------------------------

class DystopiaCameraBridge:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "angle_data": ("DICT",), # QwenMultiAngleからの出力
                "movement_type": (["Zoom In", "Pan Left", "Orbit", "Dolly Zoom"],),
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0}),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "PROMPT_STR")
    FUNCTION = "apply_camera_logic"
    CATEGORY = "Dystopia/Camera"

    def apply_camera_logic(self, angle_data, movement_type, intensity):
        # Qwen3-VL 向けのプロンプト文字列を生成
        # 例: "A shot from -30 degrees, camera zooming in slowly..."
        prompt = f"A shot from {angle_data['yaw']} degrees, {movement_type} at intensity {intensity}"
        
        # 内部的には Wan 2.6 のサンプリング条件(Conditioning)を調整するロジック
        # ... (実際のテンソル操作コード) ...
        
        return (None, prompt)
