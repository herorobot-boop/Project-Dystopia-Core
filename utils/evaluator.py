import json
import random
from pathlib import Path
from thought_generator import generate_thought

# --- モード設定 ---
# True: 過去の高スコア変異を優先 / False: 完全にランダムな変異
SELECTIVE_MODE = True 

BASE_PATH = Path("/workspace/Project-Dystopia-Core")
MUTATION_PATH = BASE_PATH / "config/mutation_patterns.json"
MUTATION_SCORE_PATH = BASE_PATH / "config/mutation_scores.json"

def evolve_thought(base_thought: dict, variation_id: int = 0):
    original_scene = base_thought.get("scene", "unknown")
    
    # 変異データの読み込み
    with open(MUTATION_PATH, "r", encoding="utf-8") as f:
        mutations = json.load(f)
    
    scores = {}
    if MUTATION_SCORE_PATH.exists():
        with open(MUTATION_SCORE_PATH, "r", encoding="utf-8") as f:
            scores = json.load(f)

    # 50%の確率で変異注入
    if random.random() < 0.5:
        if SELECTIVE_MODE and scores:
            # スコア上位5件から選出（エリート選択）
            sorted_muts = sorted(mutations, key=lambda m: scores.get(m, 0), reverse=True)
            mutation = random.choice(sorted_muts[:5])
            print(f"🎯 Selective Mutation: {mutation}")
        else:
            mutation = random.choice(mutations)
            print(f"✨ Random Mutation: {mutation}")
        
        mutated_scene = f"{original_scene}、{mutation}"
    else:
        mutated_scene = original_scene

    # LLMで新思想を生成
    evolved = generate_thought(mutated_scene, context_type=base_thought.get("context", "paid"), variation_id=variation_id)
    
    # 系統情報の追記
    evolved["meta"].update({
        "generation": base_thought.get("generation", 0) + 1,
        "ancestor_scene": original_scene,
        "mutation_applied": mutation if 'mutation' in locals() else None
    })
    
    return evolved
