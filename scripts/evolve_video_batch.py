import json
import random
from pathlib import Path
from datetime import datetime

# --- パス設定 ---
BASE_PATH = Path("/workspace/Project-Dystopia-Core")
LOG_PATH = BASE_PATH / "outputs/video_thought_log.jsonl"
# run_video_batch.py が読み込むディレクトリ
OUTPUT_DIR = BASE_PATH / "outputs/evolved_thoughts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- 進化設定 ---
MIN_SCORE = 8.0  # 進化の土俵に乗る最低スコア
MAX_GEN_COUNT = 8 # 1回の進化で生成する数
MUTATION_RATE = 0.6 # シーン変異が起きる確率

# 日本語プロンプト変異辞書
SCENE_MUTATIONS = [
    ("振り返る", "走り出す"),
    ("立ち尽くす", "歩き出す"),
    ("夕暮れ", "夜明け"),
    ("静かな", "ざわめく"),
    ("少女", "青年"),
    ("街角", "廃墟"),
    ("微笑む", "涙を流す"),
    ("見上げる", "見下ろす"),
    ("光", "影"),
    ("雨", "雪")
]

def load_video_thoughts():
    """動画評価ログを読み込み、スコア順にソートして返す"""
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f if line.strip()]
    return sorted(data, key=lambda x: x.get("score", 0), reverse=True)

def mutate_scene(scene):
    """思想（シーン）に遺伝的変異を加える"""
    new_scene = scene
    mutated = False
    
    # 辞書ベースの置換
    for before, after in SCENE_MUTATIONS:
        if before in new_scene and random.random() < MUTATION_RATE:
            new_scene = new_scene.replace(before, after)
            mutated = True
            
    # 置換が起きなかった場合、または確率で装飾語を追加
    if not mutated or random.random() < 0.3:
        suffixes = ["、光が溢れる", "、風が強く吹く", "、スローモーションで", "、粒子が舞う"]
        new_scene += random.choice(suffixes)
        
    return new_scene

def evolve():
    """進化プロセス実行"""
    thoughts = load_video_thoughts()
    # 上位個体を選別
    candidates = [t for t in thoughts if t.get("score", 0) >= MIN_SCORE]
    
    if not candidates:
        print(f"⚠️ スコア {MIN_SCORE} 以上の動画思想が不足しています。評価を続けてください。")
        return

    evolved_batch = []
    print(f"🧬 Selected {len(candidates)} ancestors for evolution.")

    for i in range(MAX_GEN_COUNT):
        # 親をランダム（ただし高スコアほど選ばれやすく）に選択
        parent = random.choice(candidates[:5]) 
        
        new_scene = mutate_scene(parent["scene"])
        parent_meta = parent.get("meta", {})
        
        # 時間軸の変異
        new_frames = random.choice([16, 24, 32, 48])
        new_fps = random.choice([8, 10, 12])
        new_gen = parent_meta.get("generation", 1) + 1
        
        # 新しいIDの発行
        timestamp = datetime.now().strftime("%m%d_%H%M%S")
        new_id = f"vid_evo_{timestamp}_{i:02d}"
        
        evolved_batch.append({
            "prompt_id": new_id,
            "scene": new_scene,
            "lora": parent.get("lora", "default"),
            "meta": {
                "frames": new_frames,
                "fps": new_fps,
                "generation": new_gen,
                "ancestor": parent["prompt_id"],
                "parent_score": parent["score"]
            }
        })

    # 保存（ファイル名は run_video_batch.py が最新を拾える形式）
    file_name = f"evolved_video_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    save_path = OUTPUT_DIR / file_name
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(evolved_batch, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Evolution Complete: {len(evolved_batch)} new thoughts saved to {save_path.name}")

if __name__ == "__main__":
    evolve()
