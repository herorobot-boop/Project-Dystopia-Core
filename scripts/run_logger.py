import csv
import os
from datetime import datetime

LOG_PATH = "/workspace/gdrive/MyDrive/Project-Dystopia/run_log.csv"

def log_run(scene_code, tags, description, prompt_path, notes=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tags_str = ", ".join(tags)

    row = {
        "timestamp": timestamp,
        "scene_code": scene_code,
        "tags": tags_str,
        "description": description,
        "prompt_path": prompt_path,
        "notes": notes
    }

    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["timestamp", "scene_code", "tags", "description", "prompt_path", "notes"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"📝 構成を run_log.csv に記録しました → {scene_code}")
