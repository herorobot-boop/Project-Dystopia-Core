import os
import shutil
import subprocess
from pathlib import Path

CERT_DIR = Path("/workspace/config/c2pa_certs")

def ensure_c2pa_credentials():
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    key_path = CERT_DIR / "es256_private.key"
    cert_path = CERT_DIR / "es256_certs.pem"

    if not key_path.exists() or not cert_path.exists():
        print("🔑 [C2PA] Generating ES256 self-signed certificate pair...")
        cmd = (
            f"openssl req -x509 -nodes -days 3650 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 "
            f"-keyout '{key_path}' -out '{cert_path}' "
            f"-subj '/CN=Project Dystopia H-K9 Algorithmic Media/O=Non-Real Media Authority/'"
        )
        subprocess.run(cmd, shell=True, check=True)

def sign_media_atomically(input_media_path: Path):
    ensure_c2pa_credentials()

    manifest_json = CERT_DIR / "manifest.json"
    manifest_content = f"""{{
        "claim_generator": "Project_Dystopia_v8.2",
        "title": "Trained Algorithmic Non-Real Media",
        "private_key": "{CERT_DIR / 'es256_private.key'}",
        "sign_cert": "{CERT_DIR / 'es256_certs.pem'}",
        "alg": "es256",
        "assertions": [
            {{
                "label": "c2pa.actions",
                "data": {{
                    "actions": [
                        {{
                            "action": "c2pa.created",
                            "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
                        }}
                    ]
                }}
            }},
            {{
                "label": "org.dystopia.audit",
                "data": {{
                    "synthetic_nature": "100% synthetically generated deep-learning output",
                    "adulthood_verified": true,
                    "engine": "Z-Image / Wan 2.2"
                }}
            }}
        ]
    }}"""
    manifest_json.write_text(manifest_content)

    temp_signed_path = input_media_path.with_suffix(".signed.tmp")
    cmd = f"c2patool '{input_media_path}' -m '{manifest_json}' -o '{temp_signed_path}' --force"
    res = subprocess.run(cmd, shell=True, capture_output=True)

    if res.returncode == int(0) and temp_signed_path.exists():
        shutil.move(temp_signed_path, input_media_path)
        print(f"🔒 [C2PA] Successfully signed & atomic replaced: {input_media_path.name}")
    else:
        if temp_signed_path.exists():
            temp_signed_path.unlink()
        print(f"⚠️ [C2PA] Signing failed, preserving raw file: {res.stderr.decode()}")

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/workspace/ComfyUI/output/latest.mp4")
    sign_media_atomically(target)
