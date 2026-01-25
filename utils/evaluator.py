import json
import random
import sys
from pathlib import Path

# --- 神経接続 ---
BASE_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = BASE_DIR / "core/engines"
if str(ENGINE_DIR) not in sys.path:
    sys.path.append(str(ENGINE_DIR))

try:
    from thought_generator import generate_thought
except ImportError:
    print("[-] Error: thought_generator.py not found.")

# 設定：新構造のパス
MUTATION_PATH = BASE_DIR / "config/logic/mutation_patterns.json"
MUTATION_SCORE_PATH = BASE_DIR / "config/logic/mutation_scores.json"
SELECTIVE_MODE = True 

def evolve_thought(base_thought: dict, variation_id: int = 0):
    """
    [HERO's Genetic Logic: 50%の確率で変異を注入し、スコア上位からエリート選択を行う]
    """
    original_scene = base_thought.get("scene", "unknown")
    
    # 変異データの読み込み
    mutations = ["noise", "glitch"] # デフォルト
    if MUTATION_PATH.exists():
        with open(MUTATION_PATH, "r", encoding="utf-8") as f:
            mutations = json.load(f)
    
    scores = {}
    if MUTATION_SCORE_PATH.exists():
        with open(MUTATION_SCORE_PATH, "r", encoding="utf-8") as f:
            scores = json.load(f)

    # 50%の確率で変異注入
    mutation = None
    if random.random() < 0.5:
        if SELECTIVE_MODE and scores:
            # スコア上位から選出（エリート選択）
            sorted_muts = sorted(mutations, key=lambda m: scores.get(m, 0), reverse=True)
            mutation = random.choice(sorted_muts[:5])
            print(f"🎯 Selective Mutation Selected: {mutation}")
        else:
            mutation = random.choice(mutations)
            print(f"✨ Random Mutation Applied: {mutation}")
        
        mutated_scene = f"{original_scene}、{mutation}"
    else:
        mutated_scene = original_scene

    # LLMで新思想を生成（依存解決済み）
    evolved = generate_thought(mutated_scene, context_type=base_thought.get("context", "paid"), variation_id=variation_id)
    
    # 系統情報の継承
    evolved["meta"].update({
        "generation": base_thought.get("meta", {}).get("generation", 0) + 1,
        "ancestor_scene": original_scene,
        "mutation_applied": mutation
    })
    
    return evolved
