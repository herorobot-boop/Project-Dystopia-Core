import json
import random
from pathlib import Path
from datetime import datetime
from thought_generator import generate_thought

# --- 設定（Project-Dystopia-Core 構成に準拠） ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
THOUGHT_LOG_PATH = BASE_PATH / "outputs/thought_log.jsonl"
EVOLVED_OUTPUT_DIR = BASE_PATH / "outputs/evolved_thoughts"
MUTATION_PATH = BASE_PATH / "config/mutation_patterns.json"

EVOLVED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- データの読み込み ---
def load_thought_log():
    thoughts = []
    if not THOUGHT_LOG_PATH.exists():
        print("❌ 思想ログが見つかりません。")
        return thoughts
    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                thoughts.append(json.loads(line))
            except: continue
    return thoughts

def load_mutation_patterns():
    """外部ファイルから変異パターンを読み込む"""
    if MUTATION_PATH.exists():
        with open(MUTATION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    print("⚠️ mutation_patterns.json が見つかりません。変異なしで進行します。")
    return []

MUTATIONS = load_mutation_patterns()

def evaluate_thoughts(thoughts: list, top_k=3):
    """スコア上位の個体を選別（エリート選択）"""
    scored = [t for t in thoughts if "score" in t]
    if scored:
        # スコア降順、同点なら新しい順
        sorted_thoughts = sorted(scored, key=lambda x: (x["score"], x.get("prompt_id", "")), reverse=True)
        print(f"💎 スコア上位 {top_k} 件を継承元として選出。")
        return sorted_thoughts[:top_k]
    else:
        print("⚠️ スコア未登録のため、最新の履歴からランダムに進化。")
        recent = thoughts[-10:] if len(thoughts) > 10 else thoughts
        return random.sample(recent, k=min(top_k, len(recent)))

def evolve_thought(base_thought: dict, variation_id: int = 0):
    """変異注入と再構築"""
    original_scene = base_thought.get("scene", "unknown")

    # 50%の確率で変異（Mutation）を発生させる
    if MUTATIONS and random.random() < 0.5:
        mutation = random.choice(MUTATIONS)
        mutated_scene = f"{original_scene}、{mutation}"
        print(f"✨ 変異注入: {mutation}")
    else:
        mutated_scene = original_scene

    context_type = base_thought.get("context", "paid")
    
    # LLMによる新世代の思想生成
    evolved = generate_thought(mutated_scene, context_type=context_type, variation_id=variation_id)
    
    # 系統情報の付与
    evolved["meta"]["generation"] = base_thought.get("generation", 0) + 1
    evolved["meta"]["ancestor_id"] = base_thought.get("prompt_id", "root")
    evolved["meta"]["ancestor_scene"] = original_scene
    evolved["meta"]["ancestor_score"] = base_thought.get("score", "N/A")
    
    return evolved

def run_evolution():
    print("🧬 Phase XIX: 思想進化プロセス（Integrated Selection & Mutation）")
    
    thoughts = load_thought_log()
    if not thoughts: return

    # 1. 優秀な個体の選別
    selected = evaluate_thoughts(thoughts, top_k=3)
    
    # 2. 進化と保存
    for idx, base in enumerate(selected):
        new_thought = evolve_thought(base, variation_id=idx)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = EVOLVED_OUTPUT_DIR / f"evolved_{timestamp}_{idx}.json"
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(new_thought, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 次世代思想 [Gen {new_thought['meta']['generation']}] を保存: {out_path.name}")

if __name__ == "__main__":
    run_evolution()
