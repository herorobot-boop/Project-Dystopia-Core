#!/usr/bin/env python3
import os
import subprocess
import requests
from pathlib import Path

CIVITAI_TOKEN = os.environ.get("CIVITAI_API_TOKEN", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

COMFY_DIR = Path("/workspace/ComfyUI")
COMFY_MODEL_DIR = COMFY_DIR / "models"
BASE_MODEL_DIR = Path("/workspace/models")

TARGET_DIRS = {
    "llm": BASE_MODEL_DIR / "llm",
    "vlm": BASE_MODEL_DIR / "vlm",
    "checkpoints": COMFY_MODEL_DIR / "checkpoints",
    "diffusion_models": COMFY_MODEL_DIR / "diffusion_models",
    "text_encoders": COMFY_MODEL_DIR / "text_encoders",
    "vae": COMFY_MODEL_DIR / "vae",
    "clip_vision": COMFY_MODEL_DIR / "clip_vision",
    "loras": COMFY_MODEL_DIR / "loras",
}
for p in TARGET_DIRS.values():
    p.mkdir(parents=True, exist_ok=True)


def verify_file(file_path: Path) -> bool:
    if not file_path.exists() or file_path.stat().st_size == 0:
        return False
    with open(file_path, "rb") as f:
        magic = f.read(512).lower()
        if b"<html" in magic or b"<!doc" in magic or b"unauthorized" in magic:
            print(f"[File Corrupt] Auth Gate detected: {file_path.name}")
            file_path.unlink()
            return False
    return True


def fetch_civitai(model_version_id: str, dest_dir: Path, filename: str):
    output_path = dest_dir / filename
    if output_path.exists() and verify_file(output_path):
        print(f"[Exist] Civitai: {filename}")
        return
    print(f"[Downloading Civitai] {filename} (ID: {model_version_id})...")
    url = f"https://civitai.red/api/download/models/{model_version_id}?type=Model&format=SafeTensor"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Authorization": f"Bearer {CIVITAI_TOKEN}" if CIVITAI_TOKEN else "",
    }
    session = requests.Session()
    res = session.get(url, headers=headers, allow_redirects=False, timeout=15)
    download_url = res.headers.get("Location") if res.status_code in (301, 302, 307, 308) else url
    fetch_headers = {"User-Agent": headers["User-Agent"]} if "amazonaws.com" in download_url else headers
    tmp_path = output_path.with_suffix(".tmp")
    with session.get(download_url, headers=fetch_headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
    tmp_path.rename(output_path)
    print(f"[SUCCESS] Civitai Model ready: {filename}")


def fetch_hf(url: str, dest_dir: Path, filename: str):
    output_path = dest_dir / filename
    if output_path.exists() and verify_file(output_path):
        print(f"[Exist] HF: {filename}")
        return
    print(f"[Downloading HF] {filename}...")
    auth = f'--header="Authorization: Bearer {HF_TOKEN}"' if HF_TOKEN else ""
    cmd = (
        f"aria2c -x 16 -s 16 -k 1M {auth} --console-log-level=warn "
        f"-c -d '{dest_dir}' -o '{filename}' '{url}'"
    )
    subprocess.run(cmd, shell=True, check=True)
    print(f"[SUCCESS] HF Model ready: {filename}")


def setup_all_assets():
    print("[H-K9] 兵站確保シークエンス開始")

    # 1. 思考層: Saluki-27B（MTP/Abliterated GGUF）
    fetch_hf(
        "https://huggingface.co/Kujira/Underdog-Saluki-27B-1.0-MTP-Abliterated-GGUF/resolve/main/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf",
        TARGET_DIRS["llm"],
        "Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf",
    )

    # 2. 視覚検品層: Qwen2.5-VL-7B + mmproj
    fetch_hf(
        "https://huggingface.co/cxtb/Qwen2.5-VL-7B-Instruct-Q8_0-GGUF/resolve/main/qwen2.5-vl-7b-instruct-q8_0.gguf",
        TARGET_DIRS["vlm"],
        "qwen2.5-vl-7b-instruct-q8_0.gguf",
    )
    fetch_hf(
        "https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/mmproj-F16.gguf",
        TARGET_DIRS["vlm"],
        "mmproj-F16.gguf",
    )

    # 3. T2I 着衣現像段: Fluxed Up + aidmaNSFWunlock
    fetch_civitai(1997816, TARGET_DIRS["checkpoints"], "fluxed_up_5.1_fp8.safetensors")
    fetch_civitai(754298, TARGET_DIRS["loras"], "aidmaNSFWunlock-FLUX-V0.2.safetensors")

    # 4. 差分編集段: Qwen-Image-Edit-2509 + 脱衣 Edit LoRA（軍律15: 低強度で併用）
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Qwen-Image-Edit/resolve/main/qwen_image_edit_2509_fp8.safetensors",
        TARGET_DIRS["diffusion_models"],
        "qwen_image_edit_2509_fp8.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/starsfriday/Qwen-Image-Edit-Remove-Clothes/resolve/main/Qwen-Image-Edit-Remove-Clothes.safetensors",
        TARGET_DIRS["loras"],
        "qwen_image_edit_remove_clothes.safetensors",
    )

    # 5. 動画化段: Wan 2.2 I2V（4090 は 5B、5090 は 14B 2段）
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_5B_fp16.safetensors",
        TARGET_DIRS["diffusion_models"],
        "wan2.2_i2v_5B_fp16.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
        TARGET_DIRS["diffusion_models"],
        "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
        TARGET_DIRS["diffusion_models"],
        "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/lightx2v/Wan2.2-Lightning/resolve/main/Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1/high_noise_model.safetensors",
        TARGET_DIRS["loras"],
        "wan22_i2v_lightning_high.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/lightx2v/Wan2.2-Lightning/resolve/main/Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1/low_noise_model.safetensors",
        TARGET_DIRS["loras"],
        "wan22_i2v_lightning_low.safetensors",
    )

    # 6. 共通: テキストエンコーダ / VAE / CLIP Vision
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        TARGET_DIRS["text_encoders"],
        "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
        TARGET_DIRS["vae"],
        "wan_2.1_vae.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
        TARGET_DIRS["clip_vision"],
        "clip_vision_h.safetensors",
    )

    # 7. extra_model_paths.yaml（v8.5 の文字列破損を修正）
    yaml_text = """comfyui:
    base_path: /workspace/models
    llm: llm/
    vlm: vlm/
"""
    (COMFY_DIR / "extra_model_paths.yaml").write_text(yaml_text)
    print("[H-K9] 兵站確保 完了")


if __name__ == "__main__":
    setup_all_assets()
