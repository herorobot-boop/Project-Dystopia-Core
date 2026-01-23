import json
import random
from pathlib import Path
from datetime import datetime
from thought_generator import generate_thought

# --- 設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
THOUGHT_LOG_PATH = BASE_PATH / "outputs/thought_log.jsonl"
EVOLVED_OUTPUT_DIR = BASE_PATH / "outputs/evolved_thoughts"
MUTATION_PATH = BASE_PATH / "config/mutation_patterns.json"
MUTATION_SCORE_PATH = BASE_PATH / "config/mutation_scores.json"

EVOLVED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def evolve_thought(base_thought: dict, variation_id: int = 0):
    original_scene = base_thought.get("scene", "unknown")
    mutations = load_json(MUTATION_PATH)
    scores = load_json(MUTATION_SCORE_PATH)

    # 50%の確率で変異注入
    if mutations and random.random() < 0.5:
        if scores:
            # スコアがある変異を優先（重み付け選択）
            # スコア上位5件＋未評価のものからランダムに選ぶことで「探索と利用」を両立
            scored_mutations = sorted(mutations, key=lambda m: scores.get(m, 0), reverse=True)
            top_pool = scored_mutations[:5]
            mutation = random.choice(top_pool)
            print(f"🎯 選択的変異(Score Optimized): {mutation}")
        else:
            mutation = random.choice(mutations)
            print(f"✨ ランダム変異: {mutation}")
        
        mutated_scene = f"{original_scene}、{mutation}"
    else:
        mutated_scene = original_scene

    evolved = generate_thought(mutated_scene, context_type=base_thought.get("context", "paid"), variation_id=variation_id)
    
    # メタデータ継承
    evolved["meta"].update({
        "generation": base_thought.get("generation", 0) + 1,
        "ancestor_id": base_thought.get("prompt_id", "root"),
        "ancestor_scene": original_scene,
        "ancestor_score": base_thought.get("score", "N/A")
    })
    
    return evolved

# (run_evolution 関数は以前のままでOK)
