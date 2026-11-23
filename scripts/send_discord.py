"""生成動画をDiscord Webhookへ通知する。未設定時はパイプラインを止めずスキップ。"""
import os
from pathlib import Path

import requests

WEBHOOK_FILE = Path("/workspace/config/discord_webhook.txt")


def _get_webhook_url() -> str:
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if url:
        return url
    if WEBHOOK_FILE.exists():
        return WEBHOOK_FILE.read_text(encoding="utf-8").strip()
    return ""


def send_video_to_discord(video_path: str, caption: str = "") -> bool:
    webhook_url = _get_webhook_url()
    if not webhook_url:
        print("ℹ️ [Discord] Webhook未設定のため通知をスキップします")
        return False

    path = Path(video_path)
    if not path.exists():
        print(f"⚠️ [Discord] 送信対象ファイルが見つかりません: {path}")
        return False

    content = caption[:1900]
    size_mb = path.stat().st_size / (1024 * 1024)

    try:
        if size_mb > 24.0:
            print(f"⚠️ [Discord] ファイルサイズ超過 ({size_mb:.1f}MB) のためテキストのみ通知")
            res = requests.post(webhook_url, json={"content": f"{content}\n(ファイル保存済: {path.name})"}, timeout=30)
        else:
            with open(path, "rb") as f:
                res = requests.post(
                    webhook_url,
                    data={"content": content},
                    files={"file": (path.name, f, "video/mp4")},
                    timeout=120,
                )
        res.raise_for_status()
        print(f"📨 [Discord] 通知完了: {path.name}")
        return True
    except Exception as exc:
        print(f"⚠️ [Discord] 送信失敗（処理は続行）: {exc}")
        return False
