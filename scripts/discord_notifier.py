#!/usr/bin/env python3
"""Discord Webhook へ成果物を直撃送信する。

25MB超過時はメタデータのみ送信する。
"""
import os
import sys
from pathlib import Path

import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
LIMIT_MB = 24.0


def send_video_to_discord(video_path_str: str, caption: str = "") -> bool:
    if not WEBHOOK_URL:
        print("💡 DISCORD_WEBHOOK_URL 未設定のため通知をスキップします。")
        return False

    video_path = Path(video_path_str)
    if not video_path.exists():
        print(f"⚠️ ファイルが存在しません: {video_path}")
        return False

    size_mb = video_path.stat().st_size / (1024 * 1024)
    if size_mb > LIMIT_MB:
        print(f"⚠️ ファイルサイズ超過 ({size_mb:.1f}MB)。メタデータのみ送信します。")
        payload = {"content": f"🎬 **動画生成完了 (容量大)**: `{video_path.name}`\n{caption}"}
        try:
            requests.post(WEBHOOK_URL, json=payload, timeout=20)
        except Exception as exc:
            print(f"⚠️ Discord送信エラー: {exc}")
            return False
        return True

    payload = {"content": f"🎬 **新作微動動画 着弾**: `{video_path.name}`\n{caption}"}
    try:
        with open(video_path, "rb") as handle:
            files = {"file": (video_path.name, handle, "video/mp4")}
            res = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=180)
    except Exception as exc:
        print(f"⚠️ Discord送信エラー: {exc}")
        return False

    if res.status_code in (200, 204):
        print("📲 [Discord] スマホへ動画プッシュ通知完了。")
        return True

    print(f"⚠️ Discord送信エラー: {res.status_code}")
    return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > int(1) else "/workspace/ComfyUI/output/latest.mp4"
    cap = sys.argv[2] if len(sys.argv) > int(2) else "Wan 2.2 微動生成完了"
    raise SystemExit(0 if send_video_to_discord(target, cap) else 1)
