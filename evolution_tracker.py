import json
from pathlib import Path
from collections import Counter

THOUGHT_LOG_PATH = Path("/workspace/Project-Dystopia/outputs/thought_log.jsonl")

def analyze_evolution():
    if not THOUGHT_LOG_PATH.exists():
        print("❌ ログが見つかりません。")
        return

    logs = []
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            logs.append(json.loads(line))

    total = len(logs)
    scored = [l for l in logs if "score" in l]
    
    print(f"📊 --- Project Dystopia: 進化統計レポート ---")
    print(f"総生成数: {total} | 評価済み: {len(scored)}")
    
    if scored:
        avg_score = sum(s["score"] for s in scored) / len(scored)
        print(f"平均審美スコア: {avg_score:.2f} / 10.0")
        
        # スコア分布
        scores = [s["score"] for s in scored]
        dist = Counter(scores)
        print("\n[スコア分布]")
        for s in range(10, 0, -1):
            bar = "█" * dist.get(s, 0)
            print(f"{s:2}点: {bar} ({dist.get(s, 0)})")

    # シーンキーワードの頻出傾向
    print("\n[頻出シーンキーワード]")
    scenes = [l["scene"] for l in logs]
    words = []
    for s in scenes:
        words.extend(s.replace("、", " ").split())
    common_words = Counter(words).most_common(5)
    for word, count in common_words:
        print(f"- {word}: {count}回採用")

    print("\n--- レポート完了 ---")

if __name__ == "__main__":
    analyze_evolution()
