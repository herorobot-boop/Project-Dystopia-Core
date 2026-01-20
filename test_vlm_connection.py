import requests
import json

VLM_URL = "http://localhost:8000/v1/chat/completions"

def test_vlm():
    payload = {
        "model": "llava",
        "messages": [
            {"role": "user", "content": "この画像には何が写っていますか？"}
        ],
        "temperature": 0.2,
        "max_tokens": 100,
        "image": "test.jpg"  # ここに画像パスを指定（Base64またはパス）
    }

    try:
        res = requests.post(VLM_URL, json=payload)
        print("✅ 接続成功")
        print(res.json())
    except Exception as e:
        print(f"❌ 接続失敗: {e}")

if __name__ == "__main__":
    test_vlm()
