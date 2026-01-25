import json
import requests
import sys
from pathlib import Path

# --- 神経接続：プロジェクトルートの特定 ---
BASE_DIR = Path(__file__).resolve().parents[2]

# --- 依存モジュールのパス追加 (utils, core/engines) ---
for path in [BASE_DIR / "utils", BASE_DIR / "core/engines"]:
    if str(path) not in sys.path:
        sys.path.append(str(path))

# 旧コードで core.mapping 等となっていたものを、新構造に合わせてインポート
try:
    from mapping import apply_mapping
    # io_utils.py はルート直下または utils にある想定で調整
    import io_utils 
except ImportError as e:
    print(f"[-] Warning: Module import failed: {e}")

# --- 設定の読み込み ---
# 本来は config/logic/vllm_config.yaml 等から読むべきですが、
# 一旦コード内で完結させつつ、将来的に config フォルダを参照する土台を作ります
VLLM_URL = "http://localhost:11434/v1/chat/completions" # Ollama/vLLM標準
MODEL_NAME = "chronos-hermes-13b"

def generate_thought(user_input, temperature=0.8):
    """
    入力された思想を構造化JSONとして出力させる
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system", 
                "content": "あなたは映像監督です。入力された思想を構造化JSONで出力してください。出力形式は有効なJSONのみとすること。"
            },
            {"role": "user", "content": user_input}
        ],
        "temperature": temperature
    }
    try:
        response = requests.post(VLLM_URL, json=payload, timeout=60)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # JSON以外の余計なテキストを排除するクリーニング処理
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(content)
    except Exception as e:
        return {"error": f"Thought generation failed: {str(e)}"}

def fuse_thoughts(self_prompt, external_prompt, temperature=0.85):
    """
    自己思想と外部思想を融合し、新たな1文を生成する
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "あなたは映像監督です。2つの思想を融合させた新しい思想を1つ生成してください。\n\n"
                    f"自己思想: 「{self_prompt}」\n"
                    f"外部思想: 「{external_prompt}」\n\n"
                    "→ 出力形式: 新しい思想（自然文1文）のみを出力せよ。"
                )
            }
        ],
        "temperature": temperature
    }

    try:
        response = requests.post(VLLM_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ LLMエラー: {str(e)}"

if __name__ == "__main__":
    # テスト実行
    test_input = "雨の廃墟で踊るアンドロイド"
    print(f"[*] Testing generate_thought with: {test_input}")
    result = generate_thought(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
