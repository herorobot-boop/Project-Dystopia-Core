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
    """
    全履歴を読み込む。
    """
    thoughts = []
    if not THOUGHT_LOG_PATH.exists():
        print("❌ thought_log.jsonl が見つかりません。生成と評価を先に行ってください。")
        return thoughts

    with open(THOUGHT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                thoughts.append(json.loads(line))
            except:
                continue
    return thoughts

def evaluate_thoughts(thoughts: list, top_k=3):
    """
    評価フェーズ：スコアが高い個体を最優先で選出。
    スコアがない場合は最新の個体からランダムに選ぶ。
    """
    # スコアがついているものだけを抽出
    scored = [t for t in thoughts if "score" in t]
    
    if scored:
        # スコア（10〜1）の降順でソート
        sorted_thoughts = sorted(scored, key=lambda x: x["score"], reverse=True)
        print(f"💎 スコア上位 {top_k} 件を継承元として選出しました。")
        return sorted_thoughts[:top_k]
    else:
        # スコアがまだ無い場合は、直近の10件からランダム選出（初期多様性）
        print("⚠️ スコアが見つかりません。直近の履歴からランダムに進化させます。")
        recent = thoughts[-10:] if len(thoughts) > 10 else thoughts
        return random.sample(recent, k=min(top_k, len(recent)))

def evolve_thought(base_thought: dict, variation_id: int = 0):
    """
    選ばれた思想をベースに、新たな変異を加えて次世代を召喚する。
    """
    original_scene = base_thought.get("scene", "unknown")
    
    # --- 変異因子：環境・質感のランダム注入 ---
    mutations = [
        "、濡れた肌の質感と透過感", 
        "、広角レンズによるパース強調", 
        "、逆光によるシルエットの強調", 
        "、極限までクローズアップした視点",
        "、粒子感のあるモノクローム調",
        "、淡いレンズフレアの干渉"
    ]
    
    # 50%の確率で変異（Mutation）を発生させる
    if random.random() < 0.5:
        mutated_scene = original_scene + random.choice(mutations)
        print(f"✨ 変異発生: {mutated_scene}")
    else:
        mutated_scene = original_scene

    # 元のコンテキスト（paid/teaserなど）を継承
    context_type = base_thought.get("context", "paid")

    # 新たな思想をLLMエンジンで再生成
    evolved = generate_thought(mutated_scene, context_type=context_type, variation_id=variation_id)
    
    # 進化系統のメタデータを付与
    evolved["meta"]["generation"] = base_thought.get("generation", 0) + 1
    evolved["meta"]["ancestor_id"] = base_thought.get("prompt_id", "root")
    evolved["meta"]["ancestor_score"] = base_thought.get("score", "N/A")
    
    return evolved

def run_evolution():
    print("🧬 Phase XVI: 思想進化プロセス（Score-based Selection）")
    
    thoughts = load_thought_log()
    if not thoughts:
        return

    # 1. 優秀な個体の選別（エリート選択）
    selected = evaluate_thoughts(thoughts, top_k=3)
    
    # 2. 進化と保存
    for idx, base in enumerate(selected):
        new_thought = evolve_thought(base, variation_id=idx)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = EVOLVED_OUTPUT_DIR / f"evolved_{timestamp}_{idx}.json"
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(new_thought, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 次世代思想 [Gen {new_thought['meta']['generation']}] を保存: {out_path.name}")

    print("\n🌿 儀式完了。進化個体は 'run_evolved_batch.py' で召喚可能です。")

if __name__ == "__main__":
    run_evolution()
