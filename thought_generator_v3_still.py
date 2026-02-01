# Project Dystopia - Still Image Production Engine (Z-Image Optimized)

class StillImageEngine:
    def __init__(self):
        # 5090 Blackwell 専用フラグ
        self.launch_args = "--nvfp4 --bf16-storage --expandable-segments"
        
    def generate_params(self, kai_code):
        """
        「改」コードに基づき、Z-Image用の低Denoise・高Steps設定を返す
        """
        # Z-Imageは低CFG(3.5-5.0)で真価を発揮する
        base_cfg = 4.5
        # Z-ImageではDenoiseは従来の60%程度に抑えるのが「正解」
        kai_mapping = {
            "改09": {"denoise": 0.45, "physics": "extreme_indentation"},
            "改10": {"denoise": 0.35, "physics": "lens_distortion_pov"}
        }
        
        target = kai_mapping.get(kai_code, {"denoise": 0.4, "physics": "standard"})
        return f"CFG: {base_cfg}, Denoise: {target['denoise']}, Physics: {target['physics']}"

# 執行
still_engine = StillImageEngine()
