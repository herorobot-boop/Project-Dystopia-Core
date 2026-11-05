#!/usr/bin/env python3
import os
import sys
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
    "unet": COMFY_MODEL_DIR / "unet",
    "diffusion_models": COMFY_MODEL_DIR / "diffusion_models",
    "text_encoders": COMFY_MODEL_DIR / "text_encoders",
    "vae": COMFY_MODEL_DIR / "vae",
    "clip_vision": COMFY_MODEL_DIR / "clip_vision",
    "loras": COMFY_MODEL_DIR / "loras",
}

def run_cmd(cmd):
    print(f"🚀 [Logistics] Executing: {cmd}")
    subprocess.run(cmd, shell=True, executable='/bin/bash', check=True)

def verify_file(file_path: Path) -> bool:
    if not file_path.exists() or file_path.stat().st_size == int(0):
        return False
    with open(file_path, "rb") as f:
        magic_bytes = f.read(512).lower()
        if b"<html" in magic_bytes or b"<!doc" in magic_bytes or b"unauthorized" in magic_bytes:
            print(f"❌ [CRITICAL] File corrupt or HTML Auth Gate detected: {file_path}")
            file_path.unlink()
            return False
    return True

def fetch_civitai_secure(model_version_id: str, output_path: Path):
    if output_path.exists() and verify_file(output_path):
        print(f"✅ [Exist] Civitai Asset verified: {output_path.name}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    initial_url = f"https://civitai.red/api/download/models/{model_version_id}?type=Model&format=SafeTensor"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Authorization": f"Bearer {CIVITAI_TOKEN}" if CIVITAI_TOKEN else ""
    }

    print(f"📥 [Downloading Civitai.red] Version ID: {model_version_id} -> {output_path.name}")
    session = requests.Session()
    res = session.get(initial_url, headers=headers, allow_redirects=False, timeout=15)

    if res.status_code in (301, 302, 307, 308):
        download_url = res.headers["Location"]
    elif res.status_code == 200:
        download_url = initial_url
    else:
        raise RuntimeError(f"Civitai API Error: HTTP {res.status_code}")

    fetch_headers = {"User-Agent": headers["User-Agent"]} if "amazonaws.com" in download_url else headers

    tmp_path = output_path.with_suffix(".tmp")
    with session.get(download_url, headers=fetch_headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
    tmp_path.rename(output_path)

    if not verify_file(output_path):
        raise ValueError(f"Civitai Download verification failed for {output_path.name}")
    print(f"✅ [SUCCESS] Civitai Model deployed: {output_path}")

def fetch_hf_direct(url: str, output_path: Path):
    if output_path.exists() and verify_file(output_path):
        print(f"✅ [Exist] HF Asset verified: {output_path.name}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 [Downloading HF] {output_path.name}...")

    auth_header = f'--header="Authorization: Bearer {HF_TOKEN}"' if HF_TOKEN else ''
    aria2_check = subprocess.run("which aria2c", shell=True, capture_output=True)
    if aria2_check.returncode == int(0):
        cmd = f"aria2c -x 16 -s 16 -k 1M {auth_header} --console-log-level=warn -c -d '{output_path.parent}' -o '{output_path.name}' '{url}'"
    else:
        cmd = f"wget -c {auth_header} '{url}' -O '{output_path}'"

    run_cmd(cmd)
    if not verify_file(output_path):
        raise ValueError(f"HF Download failed or corrupt: {url}")

def setup_all_missing_assets():
    print("🐺 [H-K9] 兵站確保シークエンス開始：全実弾モデルの直撃ダウンロードを開始します。")
    for p in TARGET_DIRS.values():
        p.mkdir(parents=True, exist_ok=True)

    # 1. 脳 (Underdog-Saluki-27B-1.0-MTP-Abliterated GGUF: 約8.35GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'Kujira'}/Underdog-Saluki-27B-1.0-MTP-Abliterated-GGUF/resolve/main/{'Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf'}",
        TARGET_DIRS["llm"] / "Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"
    )

    # 2. 眼 (Qwen2.5-VL-7B-Instruct GGUF: 約7.5GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'cxtb'}/Qwen2.5-VL-7B-Instruct-Q8_0-GGUF/resolve/main/qwen2.5-vl-7b-instruct-q8_0.gguf",
        TARGET_DIRS["vlm"] / "qwen2.5-vl-7b-instruct-q8_0.gguf"
    )

    # 3. 視覚プロジェクター (mmproj-F16.gguf: 約1.35GB) ※unsloth正規URL
    fetch_hf_direct(
        f"https://huggingface.co/{'unsloth'}/Qwen2.5-VL-7B-Instruct-GGUF/resolve/main/mmproj-F16.gguf",
        TARGET_DIRS["vlm"] / "mmproj-F16.gguf"
    )

    # 4. 構図試作 (Flux-1-Klein GGUF: 約9.3GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'city96'}/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q8_0.gguf",
        TARGET_DIRS["unet"] / "flux1-dev-Q8_0.gguf"
    )

    # 5. 究極受肉 (Z-Image-Turbo BF16: 約12.0GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'Tongyi-MAI'}/Z-Image-Turbo/resolve/main/z_image_turbo_bf16.safetensors",
        TARGET_DIRS["diffusion_models"] / "z_image_turbo_bf16.safetensors"
    )

    # 6. 動画エンジン (Wan 2.1 14B GGUF: 約9.4GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'city96'}/Wan2.1-T2V-14B-gguf/resolve/main/wan2.1-t2v-14b-Q4_K_M.gguf",
        TARGET_DIRS["diffusion_models"] / "wan2.1-t2v-14b-Q4_K_M.gguf"
    )

    # 7. 正規 Wan テキストエンコーダー (umT5 FP8 Scaled: 約5.0GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'Comfy-Org'}/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        TARGET_DIRS["text_encoders"] / "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
    )

    # 8. Wan 専用 3D-VAE (約2.6GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'Comfy-Org'}/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
        TARGET_DIRS["vae"] / "wan_2.1_vae.safetensors"
    )

    # 9. CLIP Vision (約1.2GB)
    fetch_hf_direct(
        f"https://huggingface.co/{'Comfy-Org'}/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
        TARGET_DIRS["clip_vision"] / "clip_vision_h.safetensors"
    )

    # 10. extra_model_paths.yaml の整合配備
    yaml_content = """comfyui:
    base_path: /workspace/models
    llm: llm/
    vlm: vlm/
"""
    extra_yaml = COMFY_DIR / "extra_model_paths.yaml"
    extra_yaml.write_text(yaml_content)
    print("✅ [H-K9] extra_model_paths.yaml を整合配備しました。")
    print("🎉 [H-K9] 全実弾モデルの着弾・配置が完全に完了しました。")

if __name__ == "__main__":
    setup_all_missing_assets()
