#!/usr/bin/env python3
import re, sys
from pathlib import Path

ROOT = Path("/workspace/ComfyUI/models")
pat = re.compile(r'["\']([A-Za-z0-9_.\-]+\.(?:safetensors|gguf|pt|pth|bin))["\']')
bad = set()
ALLOW_MISSING = {
    "flux1-dev-fp8.safetensors",
    "Wan2_2-TI2V-5B-Turbo_fp16.safetensors",
    "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
    "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
    "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
    "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
    "MS_Nude_Style_Flux_V2.safetensors",
    "nsfw_qwen_21.safetensors",
    "qwen_image_fp8_e4m3fn.safetensors",
}

for p in sorted(Path("scripts").glob("*.py")):
    for name in pat.findall(p.read_text(errors="ignore")):
        if name in ALLOW_MISSING:
            continue
        if not any(ROOT.rglob(name)):
            bad.add(name)
if not bad:
    print("[OK] 参照モデルは全て実在"); sys.exit(0)
print("[NG] 実在しない参照:")
for n in sorted(bad): print("  ", n)
sys.exit(1)
