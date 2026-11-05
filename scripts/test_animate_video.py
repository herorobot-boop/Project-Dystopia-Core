import os
import sys
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.comfy_api_bridge import ComfyAPIBridge
from scripts.c2pa_signer import sign_media_atomically

WORKSPACE_DIR = Path("/workspace")
WORKFLOW_DIR = WORKSPACE_DIR / "Project-Dystopia-Core/workflows"
OUTPUT_DIR = WORKSPACE_DIR / "ComfyUI/output"

def animate_chosen_image(still_filename: str, camera_motion: str = "Zoom In"):
    bridge = ComfyAPIBridge()

    bridge.sync_output_to_input(still_filename)

    video_wf_path = WORKFLOW_DIR / "wan22_fun_camera_api.json"
    with open(video_wf_path, "r", encoding="utf-8") as f:
        video_wf = json.load(f)

    prompt_data = {
        "camera_motion": camera_motion,
        "is_distilled_model": True
    }
    video_wf = bridge.inject_dynamic_parameters(video_wf, prompt_data)
    video_wf = bridge.inject_image_to_workflow(video_wf, still_filename)

    print(f"🎬 [Animating] 『{still_filename}』 を Wan 2.2 で動画化中（カメラ: {camera_motion}）...")
    video_filename = bridge.dispatch_and_wait_media(video_wf, timeout=360)
    raw_video_path = OUTPUT_DIR / video_filename

    sign_media_atomically(raw_video_path)

    print("\n" + "═"*60)
    print(f"🎉 【5秒動画 完成】: {raw_video_path}")
    print("💡 ブラウザ（Port 8188）またはJupyterLabから長押し保存できます。")
    print("═"*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > int(1):
        target_img = sys.argv[int(1)]
    else:
        images = sorted(list(OUTPUT_DIR.glob("*.png")), key=os.path.getmtime, reverse=True)
        if not images:
            print("❌ 静止画が見つかりません。先に test_critic_image.py を回してください。")
            sys.exit(1)
        target_img = images[int(0)].name

    motion = sys.argv[int(2)] if len(sys.argv) > int(2) else "Zoom In"
    animate_chosen_image(target_img, motion)
