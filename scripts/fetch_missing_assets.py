#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

CIVITAI_TOKEN = os.environ.get("CIVITAI_TOKEN", "") or os.environ.get("CIVITAI_API_TOKEN", "")
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

MIN_SIZE = 1_000_000


def verify_file(file_path: Path) -> bool:
    if not file_path.exists() or file_path.stat().st_size < MIN_SIZE:
        if file_path.exists():
            print(f"[Purge] 小さすぎ: {file_path.name} ({file_path.stat().st_size}B)")
            file_path.unlink()
        return False
    with open(file_path, "rb") as f:
        magic = f.read(512).lstrip().lower()
        if magic[:1] in (b"<", b"{") or b"unauthorized" in magic or b"access to this model" in magic:
            print(f"[Purge] 中身がHTML/JSON: {file_path.name}")
            file_path.unlink()
            return False
    return True


def fetch_civitai(model_version_id: int, target_dir: Path, filename: str) -> bool:
    target = target_dir / filename
    if verify_file(target):
        print(f"[Exist] Civitai: {filename}")
        return True
    import requests
    token = CIVITAI_TOKEN
    headers = {"Authorization": f"Bearer {token}",
               "User-Agent": "Mozilla/5.0", "Referer": "https://civitai.com/"} if token else {
               "User-Agent": "Mozilla/5.0", "Referer": "https://civitai.com/"}
    url = f"https://civitai.com/api/download/models/{model_version_id}"
    if token:
        url += f"?token={token}"
    print(f"[Downloading Civitai] {filename} (ID: {model_version_id})...")
    tmp = target.with_suffix(target.suffix + ".part")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=120, allow_redirects=True) as r:
            if r.status_code != 200:
                print(f"[WARN] Civitai HTTP {r.status_code}: {filename}")
                return False
            with tmp.open("wb") as f:
                for chunk in r.iter_content(1 << 20):
                    if chunk:
                        f.write(chunk)
    except Exception as e:
        print(f"[WARN] Civitai 例外: {e}")
        return False
    tmp.replace(target)
    if not verify_file(target):
        return False
    print(f"[SUCCESS] Civitai ready: {filename}")
    return True


def fetch_hf(url: str, dest_dir: Path, filename: str):
    output_path = dest_dir / filename
    if verify_file(output_path):
        print(f"[Exist] HF: {filename}")
        return
    print(f"[Downloading HF] {filename}...")
    auth = f'--header="Authorization: Bearer {HF_TOKEN}"' if HF_TOKEN else ""
    cmd = (
        f"aria2c -x 16 -s 16 -k 1M {auth} --console-log-level=warn --continue=true "
        f"--max-tries=5 --retry-wait=5 -c -d '{dest_dir}' -o '{filename}' '{url}'"
    )
    subprocess.run(cmd, shell=True, check=False)
    if not verify_file(output_path):
        print(f"[WARN] 取得失敗: {filename}")
        return
    print(f"[SUCCESS] HF Model ready: {filename}")


def setup_all_assets():
    print("[H-K9] 兵站確保シークエンス開始")

    fetch_hf(
        "https://huggingface.co/Kujira/Underdog-Saluki-27B-1.0-MTP-Abliterated-GGUF/resolve/main/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf",
        TARGET_DIRS["llm"],
        "Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf",
    )
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

    # T2I 土台: DAC_Fluxed_Style（Civitai 681608）
    ckpt = TARGET_DIRS["checkpoints"] / "fluxed_up_5.1_fp8.safetensors"
    if not verify_file(ckpt):
        fetch_civitai(681608, TARGET_DIRS["checkpoints"], "fluxed_up_5.1_fp8.safetensors")
    if not verify_file(ckpt):
        print("[WARN] fluxed_up 不可。Comfy-Org/flux1-dev fp8 で代替")
        fetch_hf(
            "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors",
            TARGET_DIRS["checkpoints"], "flux1-dev-fp8.safetensors",
        )

    # 着衣解除 LoRA（Civitai 検索は0件なので HF ミラー直指定）
    fetch_hf(
        "https://huggingface.co/Benrami11/aidmaNSFWunlock/resolve/main/aidmaNSFWunlock-FLUX-V0.2.safetensors",
        TARGET_DIRS["loras"], "aidmaNSFWunlock-FLUX-V0.2.safetensors",
    )

    # 差分編集段（保存名は edit_still.py の参照に合わせる）
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_fp8_e4m3fn.safetensors",
        TARGET_DIRS["diffusion_models"],
        "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
    )
   fetch_hf(
        "https://huggingface.co/TomaOmito/Qwen-Edit-2509-Lora-Remove-Clothing/resolve/main/remove_clothing.safetensors",
        TARGET_DIRS["loras"], "remove-clothes.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        TARGET_DIRS["text_encoders"], "qwen_2.5_vl_7b_fp8_scaled.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors",
        TARGET_DIRS["vae"], "qwen_image_vae.safetensors",
    )

    # 動画化段
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors",
        TARGET_DIRS["diffusion_models"], "wan2.2_ti2v_5B_fp16.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors",
        TARGET_DIRS["vae"], "wan2.2_vae.safetensors",
    )

    # 共通
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        TARGET_DIRS["text_encoders"], "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
        TARGET_DIRS["clip_vision"], "clip_vision_h.safetensors",
    )
    fetch_hf(
        "https://huggingface.co/Bingsu/adetailer/resolve/main/hand_yolov8s.pt",
        TARGET_DIRS["bbox"], "hand_yolov8s.pt",
    )

    yaml_text = """comfyui:
    base_path: /workspace/models
    llm: llm/
    vlm: vlm/
"""
    (COMFY_DIR / "extra_model_paths.yaml").write_text(yaml_text)
    import yaml as _y
    _y.safe_load((COMFY_DIR / "extra_model_paths.yaml").read_text())
    print("[H-K9] 兵站確保 完了")


if __name__ == "__main__":
    setup_all_assets()
