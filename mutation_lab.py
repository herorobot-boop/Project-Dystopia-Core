import json
import random
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

# --- 設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
THOUGHT_LOG_PATH = BASE_PATH / "outputs/thought_log.jsonl"
CHART_PATH = BASE_PATH / "outputs/mutation_score_chart.png"
MUTATION_SCORE_PATH = BASE_PATH / "config/mutation_scores.json"

def extract_mutation(scene: str, ancestor_scene: str) -> str | None:
    if not ancestor_scene or scene == ancestor_scene:
        return None
    # 差分から変異を抽出
    if scene.startswith(ancestor_scene):
        return scene[len(ancestor_scene):].strip("、 ")
    return None

def analyze_mutations():
    if not THOUGHT_LOG_PATH.exists():
        print("❌ thought_log.jsonl が見つかりません。")
        return

    logs = []
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try: logs.append(json.loads(line))
            except: continue

    mutation_data = defaultdict(list)

    for entry in logs:
        meta = entry.get("meta", {})
        ancestor_scene = meta.get("ancestor_scene") or ""
        scene = entry.get("scene", "")
        score = entry.get("score")

        if score is None: continue

        mutation = extract_mutation(scene, ancestor_scene)
        if mutation:
            mutation_data[mutation].append(score)

    if not mutation_data:
        print("⚠️ 変異パターンが検出されませんでした。")
        return

    # 平均スコアの算出とソート
    stats = {}
    for mut, scores in mutation_data.items():
        avg = sum(scores) / len(scores)
        stats[mut] = {"avg": round(avg, 2), "count": len(scores)}

    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["avg"], reverse=True)

    print("🧪 --- Project Dystopia: 変異パターン評価レポート ---")
    labels, averages = [], []
    
    # スコア辞書の更新用
    new_scores = {}

    for mut, data in sorted_stats:
        avg, count = data["avg"], data["count"]
        bar = "█" * int(avg)
        print(f"{mut:<30} | 平均: {avg:.2f} | 件数: {count:>2} | {bar}")
        labels.append(mut)
        averages.append(avg)
        new_scores[mut] = avg

    # 1. グラフ保存
    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], averages[::-1], color="skyblue")
    plt.title("Mutation Performance (Average Score)")
    plt.tight_layout()
    plt.savefig(CHART_PATH)
    print(f"\n📊 グラフを保存: {CHART_PATH.name}")

    # 2. 次世代用スコアファイルの自動生成
    with open(MUTATION_SCORE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_scores, f, indent=2, ensure_ascii=False)
    print(f"🧬 自動学習完了: {MUTATION_SCORE_PATH.name} を更新しました。")

if __name__ == "__main__":
    analyze_mutations()
