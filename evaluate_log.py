import csv

LOG_PATH = "run_log.csv"
SUCCESS_KEYWORDS = ["◎", "成功", "良好", "安定", "OK"]

def is_success(note):
    return any(key in note for key in SUCCESS_KEYWORDS)

def extract_successful_runs(log_path=LOG_PATH):
    successful = []
    with open(log_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if is_success(row["notes"]):
                successful.append(row)
    return successful

def print_summary(runs):
    print(f"✅ 成功構成一覧（{len(runs)}件）:")
    for r in runs:
        print(f"- {r['scene_code']} → {r['output_path']} | {r['notes']}")

# 実行
if __name__ == "__main__":
    results = extract_successful_runs()
    print_summary(results)
