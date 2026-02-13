import json
import re
import math
from pathlib import Path

class H_K9_PhysicalSimulator:
    def __init__(self, dict_dir="/workspace/Project-Dystopia-Core/config/dictionary/"):
        self.dict_dir = Path(dict_dir)
        self.master_data = {}
        # 物理演算の基底テンプレート
        self.base_physics_map = {
            "精液": "high-viscosity {resource_color} discharge, specular_reflection, fixation",
            "挿入": "interface coupling, {indent}mm skin indentation, structural maintenance",
            "食い込み": "extreme SQUISH indentation, {indent}mm tissue displacement, flesh overlap",
            "マン筋": "vulva indentation line, high-detail skin tension, {indent}mm depth",
            "密着": "surface-to-surface contact, zero-gap coupling, {pressure} pressure_coeff"
        }
        self.merge_dictionaries()

    def merge_dictionaries(self):
        if not self.dict_dir.exists(): return
        for json_file in sorted(self.dict_dir.glob("hk9_*.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                self.master_data.update(json.load(f))

    def compute_displacement(self, intensity=0.8):
        return {
            "indent": int(15 + 45 * (intensity ** 2)),
            "pressure": round(1.0 + (intensity * 2.0), 2),
            "squish": round(1.0 + (intensity * 1.5), 2),
            "resource_color": "pearl_white" if intensity < 0.8 else "viscous_concentrated_white"
        }

    def _apply_advanced_optics(self, text):
        if "配信" in text: return "webcam_quality, compression_artifacts, low_bitrate"
        if "夢の国" in text: return "smartphone_camera, lens_smudge, outdoor_lighting"
        if "番組" in text: return "broadcast_camera, studio_lighting, high_bitrate"
        return "raw_photo, visible_pores, 8k_uhd"

    def translate(self, user_input, intensity=0.8):
        phys = self.compute_displacement(intensity)
        scenario = ""
        matched_mod = None
        
        # 辞書スキャン
        for key, val in self.master_data.items():
            if key == "modifications":
                for m_key, m_val in val.items():
                    if m_key in user_input: matched_mod = m_val
                continue
            if key in user_input: scenario = val if isinstance(val, str) else str(val)

        # 物理置換
        core_prompt = f"{scenario} {user_input}"
        for jp, en in self.base_physics_map.items():
            if jp in core_prompt:
                core_prompt = core_prompt.replace(jp, en.format(**phys))
        
        optics = self._apply_advanced_optics(core_prompt)
        mod_tags = f"({matched_mod['effect']}:1.4), ({matched_mod['physics']}:{phys['squish']})" if matched_mod else ""

        return {
            "positive": f"HK9_SIM_DATA: {optics}, {mod_tags}, {core_prompt}, (flesh_squish:{phys['squish']}), phys_engine_output",
            "negative": "illustration, 3d render, plastic, clean skin, (human:1.3)",
            "denoise": matched_mod.get("denoise", 0.42) if matched_mod else 0.42,
            "cfg": 4.5 + (intensity * 1.5)
        }
