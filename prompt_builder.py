import os
import json
from datetime import datetime
from prompt_engine import PromptEngine

OUTPUT_DIR = "/workspace/gdrive/MyDrive/Project-Dystopia/RunPayloads/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_prompt(payload):
    engine = PromptEngine()
    return engine.build(payload)

def save_prompt(prompt, scene_code):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"prompt_{scene_code}_{timestamp}.json"
    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(prompt, f, indent=2, ensure_ascii=False)
    return out_path
