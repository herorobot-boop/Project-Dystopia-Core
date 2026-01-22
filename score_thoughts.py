import json
from pathlib import Path

# --- 設定 ---
THOUGHT_LOG_PATH = Path("/workspace/Project-Dystopia/outputs/thought_log.jsonl")

def score_thoughts():
    if not THOUGHT_LOG_PATH.exists():
        print("❌ 思想ログが見つかりません。まず result_watcher.py を実行してください。")
        return

    # ログを一旦すべて読み込む
    all_entries = []
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            all_entries.append(json.loads(line))

    updated_entries = []
    has_update = False

    print("⚖️ --- Project Dystopia: 審判の刻 ---")
    print("画像を見て、1〜10のスコアを入力してください（Enterでスキップ、qで終了）\n")

    for entry in all_entries:
        # すでにスコアがある場合はスキップ
        if "score" in entry:
            updated_entries.append(entry)
            continue

        prompt_id = entry.get("prompt_id")
        img_path = entry.get("image_path")
        scene = entry.get("scene")

        print(f"ID: {prompt_id}")
        print(f"SCENE: {scene}")
        print(f"IMAGE: {img_path}")
        
        val = input(">>> Score (1-10): ").strip()

        if val.lower() == 'q':
            # 残りの未評価分を保持して終了
            remaining_index = all_entries.index(entry)
            updated_entries.extend(all_entries[remaining_index:])
            break
        
        if val.isdigit():
            score = int(val)
            entry["score"] = score
            has_update = True
            print(f"⭐ Score {score} を記録しました。")
        else:
            print("⏩ スキップしました。")
        
        updated_entries.append(entry)
        print("-" * 30)

    if has_update:
        # ログファイルを上書き保存
        with open(THOUGHT_LOG_PATH, "w", encoding="utf-8") as f:
            for entry in updated_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print("\n✅ 全ての評価を思想ログに刻みました。")
    else:
        print("\n👋 更新はありませんでした。")

if __name__ == "__main__":
    score_thoughts()
