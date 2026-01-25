import json
from pathlib import Path
from collections import Counter

# 新構造のログパス
BASE_DIR = Path(__file__).resolve().parents[1]
THOUGHT_LOG_PATH = BASE_DIR / "outputs/payload_logs/thought_log.jsonl"

def analyze_evolution():
    """
    [HERO's Analytics: スコア分布の可視化と頻出キーワードの抽出]
    """
    if not THOUGHT_LOG_PATH.exists():
        print(f"[-] Log not found: {THOUGHT_LOG_PATH}")
        return

    logs = []
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except: continue

    scored = [l for l in logs if "score" in l or ("meta" in l and "score" in l["meta"])]
    
    print(f"\n📊 --- Project Dystopia: 進化統計レポート ---")
    print(f"総生成数: {len(logs)} | 評価済み: {len(scored)}")
    
    if scored:
        # スコア分布の計算
        scores = [l.get("score") or l["meta"].get("score") for l in scored]
        avg_score = sum(scores) / len(scored)
        print(f"平均審美スコア: {avg_score:.2f} / 10.0")
        
        dist = Counter(scores)
        print("\n[スコア分布]")
        for s in range(10, 0, -1):
            bar = "█" * dist.get(s, 0)
            print(f"{s:2}点: {bar} ({dist.get(s, 0)})")

    # シーンキーワードの頻出傾向
    print("\n[頻出シーンキーワード]")
    words = []
    for l in logs:
        scene = l.get("scene", "")
        words.extend(scene.replace("、", " ").split())
    
    for word, count in Counter(words).most_common(5):
        print(f"- {word}: {count}回採用")

    print("\n--- レポート完了 ---")

if __name__ == "__main__":
    analyze_evolution()
