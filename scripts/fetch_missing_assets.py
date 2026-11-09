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
    "bbox": COMFY_MODEL_DIR / "ultralytics" / "bbox",
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


def fetch_civitai(model_version_id: int, target_dir: Path, filename: str) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    if target.exists() and target.stat().st_size > 1_000_000:
        print(f"[Exist] Civitai: {filename}")
        return
    token = os.environ.get("CIVITAI_API_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"https://civitai.com/api/download/models/{model_version_id}"
    if token:
        url += f"?token={token}"
    print(f"[Downloading Civitai] {filename} (ID: {model_version_id})...")
    with requests.get(url, headers=headers, stream=True, timeout=120, allow_redirects=True) as r:
        if r.status_code != 200:
            print(f"[WARN] Civitai HTTP {r.status_code}: {filename}"); return False
        ctype = r.headers.get("Content-Type", "").lower()
        if "html" in ctype or "json" in ctype:
            print(f"[WARN] Civitai がファイル以外: {ctype} {filename}"); return False
        tmp = target.with_suffix(target.suffix + ".part")
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                if chunk:
                    f.write(chunk)
    tmp.replace(target)
    print(f"[SUCCESS] Civitai ready: {filename}")


def fetch_hf(url: str, dest_dir: Path, filename: str):
    output_path = dest_dir / filename
    if output_path.exists() and verify_file(output_path):
        print(f"[Exist] HF: {filename}")
        return
    print(f"[Downloading HF] {filename}...")
    auth = f'--header="Authorization: Bearer {HF_TOKEN}"' if HF_TOKEN else ""
    cmd = (
        f"aria2c -x 16 -s 16 -k 1M {auth} --console-log-level=warn --continue=true --max-tries=5 --retry-wait=5 "
        f"-c -d '{dest_dir}' -o '{filename}' '{url}'"
    )
    subprocess.run(cmd, shell=True, check=True)
    print(f"[SUCCESS] HF Model ready: {filename}")


def setup_all_assets():
    print("[H-K9] 兵站確保シークエンス開始")

    # 1. 思考層
    fetch_hf(
        "https://huggingface.co/Kujira/Underdog-Saluki-27B-1.0-MTP-Abliterated-GGUF/resolve/main/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf",
        TARGET_DIRS["llm"],
        "Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf",
    )

    # 2. 視覚検品層
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

    # 3. T2I 着衣現像段
    ckpt = TARGET_DIRS["checkpoints"] / "fluxed_up_5.1_fp8.safetensors"
    TARGET_DIRS["checkpoints"].mkdir(parents=True, exist_ok=True)
    if not ckpt.exists():
        fetch_civitai(1997816, TARGET_DIRS["checkpoints"], "fluxed_up_5.1_fp8.safetensors")
    if not ckpt.exists():
        print("[WARN] fluxed_up 不可。Comfy-Org/flux1-dev fp8 で代替")
        fetch_hf("https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors", TARGET_DIRS["checkpoints"], "flux1-dev-fp8.safetensors")
    fetch_civitai(754298, TARGET_DIRS["loras"], "aidmaNSFWunlock-FLUX-V0.2.safetensors")

    # 4. 差分編集段
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

    # 5. 動画化段（軍律14）
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_5B_fp16.safetensors",
        TARGET_DIRS["diffusion_models"],
        "wan2.2_i2v_5B_fp16.safetensors",
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

    # 6. 共通
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

    # 7. 手検出（自動マスク用）
    fetch_hf(
        "https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov8s.pt",
        TARGET_DIRS["bbox"],
        "hand_yolov8s.pt",
    )

    # 8. extra_model_paths.yaml（v8.5 の文字列破損を修正）
    yaml_text = """comfyui:
    base_path: /workspace/models
    llm: llm/
    vlm: vlm/
"""
    (COMFY_DIR / "extra_model_paths.yaml").write_text(yaml_text)
    try:
        import yaml as _y
        _y.safe_load((COMFY_DIR / "extra_model_paths.yaml").read_text())
    except Exception as e:
        print(f"[H-K9] YAML 検証失敗: {e}")
        raise
    print("[H-K9] 兵站確保 完了")


if __name__ == "__main__":
    setup_all_assets()
