import json
from pathlib import Path

# --- 設定 ---
THOUGHT_LOG_PATH = Path("/workspace/Project-Dystopia/outputs/thought_log.jsonl")

def load_logs():
    logs = {}
    if not THOUGHT_LOG_PATH.exists():
        return logs
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.load(line)
                logs[data["prompt_id"]] = data
            except: continue
    return logs

def trace_bloodline(target_id, logs, depth=0):
    """
    指定されたIDから祖先を遡り、系譜を表示する。
    """
    if target_id not in logs:
        if target_id == "root" or not target_id:
            print("  " * depth + "└── [Origin: 初期思想]")
        else:
            print("  " * depth + f"└── [Unknown Ancestor: {target_id}]")
        return

    entry = logs[target_id]
    score = entry.get("score", "N/A")
    scene = entry.get("scene", "Unknown")
    gen = entry.get("meta", {}).get("generation", 0)
    
    # 系譜の表示（世代が進むほどインデントを下げる）
    prefix = "└── " if depth > 0 else "👑 Root Target: "
    print("  " * depth + f"{prefix}[Gen {gen}] ID: {target_id} | Score: {score} | Scene: {scene}")

    # 祖先を遡る
    ancestor_id = entry.get("meta", {}).get("ancestor_id")
    if ancestor_id:
        trace_bloodline(ancestor_id, logs, depth + 1)

def show_all_bloodlines():
    logs = load_logs()
    if not logs:
        print("❌ ログがありません。")
        return

    # スコアが高い順（8以上）にターゲットを選出
    high_scores = [l for l in logs.values() if l.get("score", 0) >= 8]
    
    print("🧬 --- Project Dystopia: 血統の地図（Bloodline Map） ---")
    if not high_scores:
        print("💡 まだスコア8以上の個体がありません。最新の5件を表示します。")
        high_scores = list(logs.values())[-5:]

    for target in high_scores:
        print("\n" + "="*50)
        trace_bloodline(target["prompt_id"], logs)

if __name__ == "__main__":
    show_all_bloodlines()
