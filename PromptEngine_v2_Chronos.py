import requests
import json

class ChronosLLM:
    def __init__(self, endpoint, system_prompt_path, cot_protocol_path):
        self.endpoint = endpoint
        self.system_prompt = self._load_text(system_prompt_path)
        self.cot_protocol = self._load_text(cot_protocol_path)

    def _load_text(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_prompt(self, scene_seed, tags=None, user_instruction=None):
        tag_str = ", ".join(tags) if tags else "なし"
        user_input = user_instruction or f"以下の構成でシーンを設計してください：{scene_seed}（タグ: {tag_str}）"

        payload = {
            "model": "chronos-hermes",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.cot_protocol + "\n\n" + user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "stop": None
        }

        response = requests.post(self.endpoint, json=payload)
        if response.status_code != 200:
            raise Exception(f"LLM API Error: {response.status_code} - {response.text}")

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return content
