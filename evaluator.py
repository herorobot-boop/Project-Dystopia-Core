import json
import random
from pathlib import Path
from datetime import datetime
from thought_generator import generate_thought

# --- 設定 ---
THOUGHT_LOG_PATH = Path("/workspace/Project-Dystopia/outputs/thought_log.jsonl")
EVOLVED_OUTPUT_DIR = Path("/workspace/Project-Dystopia/outputs/evolved_thoughts")
EVOLVED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_thought_log():
    thoughts = []
    if not THOUGHT_LOG_PATH.exists():
        print("❌ thought_log.jsonl が見つかりません。生成を先に行ってください。")
        return thoughts

    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                thoughts.append(json.loads(line))
            except Exception as e:
                continue
    return thoughts

def evaluate_thoughts(thoughts: list, top_k=3):
    """
    評価フェーズ：現在は簡易的に『最新の成果』または『ランダム』から選出。
    将来的にはここに画像解析AIによる自動スコアや、HEROの手動評価(Rating)を紐付ける。
    """
    if len(thoughts) < top_k:
        return thoughts
    
    # 戦略的選出：最新の成功例を重視しつつ、多様性のためにランダムを混ぜる
    sorted_thoughts = sorted(thoughts, key=lambda x: x.get("timestamp", ""), reverse=True)
    seeds = sorted_thoughts[:10] # 直近10件から
    return random.sample(seeds, k=min(top_k, len(seeds)))

def evolve_thought(base_thought: dict, variation_id: int = 0):
    """
    選ばれた思想のDNA（シーン、LoRA構成）を解析し、変異（Mutation）を加える。
    """
    original_scene = base_thought.get("scene", "unknown")
    
    # --- 変異アルゴリズム：環境因子の注入 ---
    mutations = [
        "、超広角で", "、シネマティックな逆光", 
        "、肌に付着した水滴の質感", "、極限まで低いアングルから",
        "、レンズフレアの干渉", "、粒子感のあるフィルムノイズ"
    ]
    
    # 30%の確率で劇的な環境変化（変異）が発生
    if random.random() < 0.3:
        mutated_scene = original_scene + random.choice(mutations)
    else:
        mutated_scene = original_scene

    # 元のコンテキストを維持
    context_type = "paid" if "paid" in str(base_thought.get("image_path", "")) else "teaser"

    # 新たな思想の召喚（再演算）
    evolved = generate_thought(mutated_scene, context_type=context_type, variation_id=variation_id)
    
    # 進化の記録をメタデータに刻む
    evolved["meta"]["generation"] = base_thought.get("generation", 0) + 1
    evolved["meta"]["ancestor_id"] = base_thought.get("prompt_id", "root")
    
    return evolved

def run_evolution():
    print("🧬 Phase XVI: 思想の進化（Evolution）を開始します…")
    thoughts = load_thought_log()
    if not thoughts:
        return

    # 1. 優秀な個体の選別
    selected = evaluate_thoughts(thoughts, top_k=3)
    print(f"🌱 継承される個体: {[t['prompt_id'] for t in selected]}")

    # 2. 次世代の創出
    for idx, base in enumerate(selected):
        new_thought = evolve_thought(base, variation_id=idx)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = EVOLVED_OUTPUT_DIR / f"evolved_{timestamp}_{idx}.json"
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(new_thought, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 次世代思想を記録: {out_path.name}")

    print("\n🌿 進化の儀式が完了しました。これらの思想は run_batch.py で即座に実体化可能です。")

if __name__ == "__main__":
    run_evolution()
