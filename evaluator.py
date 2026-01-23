import json
import random
from pathlib import Path
from datetime import datetime
from thought_generator import generate_thought

# --- パス設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
THOUGHT_LOG_PATH = BASE_PATH / "outputs/thought_log.jsonl"
EVOLVED_OUTPUT_DIR = BASE_PATH / "outputs/evolved_thoughts"
MUTATION_PATH = BASE_PATH / "config/mutation_patterns.json"
MUTATION_SCORE_PATH = BASE_PATH / "config/mutation_scores.json"

EVOLVED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_json_data(path, default_value):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_value

def evolve_thought(base_thought: dict, variation_id: int = 0):
    original_scene = base_thought.get("scene", "unknown")
    mutations = load_json_data(MUTATION_PATH, [])
    scores = load_json_data(MUTATION_SCORE_PATH, {})

    # 50%の確率で変異注入
    if mutations and random.random() < 0.5:
        # スコアが高い上位5件 + ランダムな数件を混ぜて選定プールを作成（探索と利用の両立）
        scored_list = sorted(mutations, key=lambda m: scores.get(m, 5.0), reverse=True)
        mutation_pool = scored_list[:5] + random.sample(mutations, min(len(mutations), 2))
        mutation = random.choice(mutation_pool)
        
        mutated_scene = f"{original_scene}、{mutation}"
        print(f"✨ 選択的変異(Optimized): {mutation} (Est. Score: {scores.get(mutation, 'N/A')})")
    else:
        mutated_scene = original_scene

    # 新世代の思想を召喚
    evolved = generate_thought(mutated_scene, context_type=base_thought.get("context", "paid"), variation_id=variation_id)
    
    # 系統樹の記録
    evolved["meta"].update({
        "generation": base_thought.get("generation", 0) + 1,
        "ancestor_id": base_thought.get("prompt_id", "root"),
        "ancestor_scene": original_scene,
        "ancestor_score": base_thought.get("score", 0.0)
    })
    
    return evolved

def run_evolution():
    print("🧬 Starting Evolution Cycle...")
    # (既存の run_evolution ロジック)
    # 1. ログを読み込み、2. evaluate_thoughts で上位を選び、3. evolve_thought を回して保存。
    pass

if __name__ == "__main__":
    run_evolution()
