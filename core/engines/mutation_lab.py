import json
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import numpy as np

# --- 神経接続：新構造パスの動的特定 ---
BASE_DIR = Path(__file__).resolve().parents[2]
THOUGHT_LOG_PATH = BASE_DIR / "outputs/payload_logs/thought_log.jsonl"
CHART_PATH = BASE_DIR / "outputs/mutation_score_chart.png"
MUTATION_SCORE_PATH = BASE_DIR / "config/logic/mutation_scores.json"

MIN_SAMPLES = 2

def analyze_mutations():
    if not THOUGHT_LOG_PATH.exists(): 
        print(f"[-] No log found at {THOUGHT_LOG_PATH}")
        return
    
    logs = []
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try: logs.append(json.loads(line))
            except: continue

    mutation_data = defaultdict(list)
    for entry in logs:
        meta = entry.get("meta", {})
        anc = meta.get("ancestor_scene", "")
        cur = entry.get("scene", "")
        score = entry.get("score")
        # 差分から変異キーワードを特定する HERO's Logic
        if score is not None and anc and cur.startswith(anc) and cur != anc:
            mut = cur[len(anc):].strip("、 ")
            mutation_data[mut].append(score)

    if not mutation_data: 
        print("[-] No valid mutation data to analyze.")
        return

    stats = {}
    for mut, scores in mutation_data.items():
        if len(scores) < MIN_SAMPLES: continue 
        stats[mut] = {
            "avg": round(float(np.mean(scores)), 2),
            "count": len(scores)
        }

    # スコア順にソートし、次世代の進化パラメータ（JSON）を更新
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["avg"], reverse=True)
    new_scores = {mut: d["avg"] for mut, d in sorted_stats}
    
    with open(MUTATION_SCORE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_scores, f, indent=2, ensure_ascii=False)

    # グラフ出力（可視化）
    if sorted_stats:
        labels = [f"{m} (n={d['count']})" for m, d in sorted_stats]
        avgs = [d["avg"] for m, d in sorted_stats]
        plt.figure(figsize=(12, 8))
        plt.barh(labels[::-1], avgs[::-1], color="teal")
        plt.xlabel("Average Mutation Performance Score")
        plt.title("H-K9 Mutation Performance Analysis")
        plt.tight_layout()
        plt.savefig(CHART_PATH)
        print(f"📊 Analysis complete. Evolution scores updated: {MUTATION_SCORE_PATH.name}")

if __name__ == "__main__":
    analyze_mutations()
