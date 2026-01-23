import json
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import numpy as np

# --- 設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
THOUGHT_LOG_PATH = BASE_PATH / "outputs/thought_log.jsonl"
CHART_PATH = BASE_PATH / "outputs/mutation_score_chart.png"
MUTATION_SCORE_PATH = BASE_PATH / "config/mutation_scores.json"

# 分析の信頼性を高めるための最小試行回数
MIN_SAMPLES = 2

def analyze_mutations():
    if not THOUGHT_LOG_PATH.exists(): return
    
    logs = []
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try: logs.append(json.loads(line))
            except: continue

    mutation_data = defaultdict(list)
    for entry in logs:
        meta = entry.get("meta", {})
        # ancestor_sceneと現在のsceneの差分から変異を特定
        anc = meta.get("ancestor_scene", "")
        cur = entry.get("scene", "")
        score = entry.get("score")
        if score is not None and cur.startswith(anc) and cur != anc:
            mut = cur[len(anc):].strip("、 ")
            mutation_data[mut].append(score)

    if not mutation_data: return

    stats = {}
    for mut, scores in mutation_data.items():
        if len(scores) < MIN_SAMPLES: continue # フィルタリング
        stats[mut] = {
            "avg": round(float(np.mean(scores)), 2),
            "median": round(float(np.median(scores)), 2),
            "count": len(scores)
        }

    # スコア順にソート
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["avg"], reverse=True)
    
    # mutation_scores.json を自動生成（次世代の進化に即座に反映）
    new_scores = {mut: d["avg"] for mut, d in sorted_stats}
    with open(MUTATION_SCORE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_scores, f, indent=2, ensure_ascii=False)

    # グラフ出力
    labels = [f"{m} (n={d['count']})" for m, d in sorted_stats]
    avgs = [d["avg"] for m, d in sorted_stats]
    
    plt.figure(figsize=(12, 8))
    plt.barh(labels[::-1], avgs[::-1], color="teal")
    plt.xlabel("Average Score")
    plt.title("Mutation Performance Analysis")
    plt.tight_layout()
    plt.savefig(CHART_PATH)
    print(f"📊 Analysis complete. Data saved to {MUTATION_SCORE_PATH.name}")

if __name__ == "__main__":
    analyze_mutations()
