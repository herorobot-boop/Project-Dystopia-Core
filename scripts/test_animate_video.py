import os
import sys
import json
import subprocess
from pathlib import Path
from scripts.comfy_api_bridge import ComfyAPIBridge
from scripts.c2pa_signer import sign_media_atomically

WORKSPACE_DIR = Path("/workspace")
WORKFLOW_DIR = WORKSPACE_DIR / "Project-Dystopia-Core/workflows"
OUTPUT_DIR = WORKSPACE_DIR / "ComfyUI/output"

def animate_chosen_image(still_filename: str, camera_motion: str = "Zoom In", engine_route: str = "wan"):
    bridge = ComfyAPIBridge()

    # 1. 【軍律9】output/ から input/ への画像同期 (LoadImageのFileNotFoundError完全防止)
    bridge.sync_output_to_input(still_filename)

    # 2. エンジンルートの分岐ロード
    if engine_route.lower() == "h3":
        video_wf_path = WORKFLOW_DIR / "minimax_h3_audio_api.json"
        engine_name = "FastH3 Omni 8-Step (有音動画)"
    else:
        video_wf_path = WORKFLOW_DIR / "wan22_fun_camera_api.json"
        engine_name = "Wan 2.2 Fun Camera (幾何カメラ制御)"

    if not video_wf_path.exists():
        print(f"❌ ワークフローファイルが見つかりません: {video_wf_path}")
        print(f"💡 第1章手順5に従い、ComfyUI画面から '{video_wf_path.name}' をエクスポートしてください。")
        return

    with open(video_wf_path, "r", encoding="utf-8") as f:
        video_wf = json.load(f)

    # 3. パラメータ注入 (単一float speed & カメラモーション)
    prompt_data = {
        "camera_motion": camera_motion,
        "is_distilled_model": True
    }
    video_wf = bridge.inject_dynamic_parameters(video_wf, prompt_data)
    video_wf = bridge.inject_image_to_workflow(video_wf, still_filename)

    # 4. レンダリング監視 (images, gifs, videos 多重走査)
    print(f"\n🎬 [Animation Start] 『{still_filename}』 を {engine_name} で動画化開始...")
    print(f"🎥 [Camera Control] 指定モーション: {camera_motion} / Speed: 1.2")
    video_filename = bridge.dispatch_and_wait_media(video_wf, timeout=360)
    raw_video_path = OUTPUT_DIR / video_filename

    # 5. 【法的防壁】C2PA不可逆電子署名のアトミック注入
    print(f"\n🔒 [C2PA Signing] 成果物への非実在証明メタデータ注入中: {video_filename}")
    sign_media_atomically(raw_video_path)

    print("\n" + "═"*65)
    print(f"🎉 【動画生成・法的防壁付与 完了】")
    print(f"📁 成果物ファイル: {raw_video_path}")
    print("💡 スマホブラウザ (Port 8188) の出力ノードから長押しでカメラロールへ保存してください。")
    print("═"*65 + "\n")

if __name__ == "__main__":
    # 引数パース: python3 test_animate_video.py <画像ファイル名> <カメラモーション> <エンジン(wan/h3)>
    if len(sys.argv) > int(1):
        target_img = sys.argv[int(1)]
    else:
        # 指定がない場合は output/ 内の最新静止画を自動取得
        png_images = sorted(list(OUTPUT_DIR.glob("*.png")), key=os.path.getmtime, reverse=True)
        if not png_images:
            print("❌ 静止画が見つかりません。先に第2部の test_critic_image.py を実行してください。")
            sys.exit(int(1))
        target_img, *_ = [img.name for img in png_images]

    motion = sys.argv[int(2)] if len(sys.argv) > int(2) else "Zoom In"
    route = sys.argv[int(3)] if len(sys.argv) > int(3) else "wan"

    animate_chosen_image(target_img, motion, route)
