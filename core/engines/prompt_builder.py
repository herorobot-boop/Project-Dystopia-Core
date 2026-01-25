import json
import sys
from pathlib import Path

# --- 神経接続：プロジェクトルートの動的特定 ---
BASE_DIR = Path(__file__).resolve().parents[2]

# --- 同階層のエンジンを読み込めるように設定 ---
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

def build_prompt(thought_json: dict, negative: bool = False) -> str:
    """
    人物固定タグとLoRAタグを統合して、最終的なプロンプトを構築する。
    [HERO's Logic Preserved: 質感・干渉・生理反応の重層構造を維持]
    """
    context = thought_json.get("context_type", "free")

    # --- ネガティブプロンプト構築 (変更なし) ---
    if negative:
        base_negatives = [
            "worst quality", "low quality", "normal quality", "jpeg artifacts",
            "blurry", "bad anatomy", "bad hands", "text", "error", "watermark",
            "username", "artist name", "fused fingers", "plastic skin"
        ]
        if context == "free":
            base_negatives += ["nsfw", "nude", "cleavage", "underwear", "suggestive"]
        elif context == "paid":
            base_negatives += ["perfect symmetry", "studio lighting", "airbrushed skin", "makeup"]
        
        return ", ".join(base_negatives)

    # --- ポジティブプロンプト構築 ---
    
    # LoRAタグ
    lora_tags = [f"<lora:{l['name']}:{l['weight']}>" for l in thought_json.get("lora_settings", [])]

    # Identity（人物記述）
    identity_tags = thought_json.get("identity_tag", "1girl")

    # 構図・照明・シーン (新構造のパス経由でもデータ形式を維持)
    vc = thought_json.get("visual_config", {})
    view = vc.get("view", "").replace("_", " ")
    lighting = vc.get("lighting", "").replace("_", " ")
    focus = vc.get("focus_strategy", "").replace("_", " ")
    scene = thought_json.get("scene_context", "")

    # 質感・干渉
    fabric_logic = thought_json.get("fabric_logic", {})
    fabric = fabric_logic.get("material_interaction", "").replace("_", " ")
    action = fabric_logic.get("action_state", "").replace("_", " ")
    
    # 生理反応 (Paidのみ)
    physiology = thought_json.get("physiology_detail", "").replace("_", " ")
    if physiology:
        physiology = f"({physiology}:1.2)"

    # リアリズム・光学
    realism_tags = [t.replace("_", " ") for t in thought_json.get("realism_tags", [])]
    overrides = thought_json.get("global_overrides", {})
    optical = overrides.get("optical", "").replace("_", " ")
    physics = overrides.get("physics", "").replace("_", " ")

    # --- 最終結合（情報の重層構造：HERO's Architecture） ---
    prompt_parts = [
        *lora_tags,
        "masterpiece, best quality, photographic, sharp focus",
        scene,
        identity_tags,
        f"{view}, {lighting}, {focus}",
        f"{fabric}, {action}",
        physiology,
        ", ".join(realism_tags),
        optical,
        physics
    ]

    final_prompt = ", ".join([p for p in prompt_parts if p and p.strip()])
    return final_prompt.replace("_", " ").strip()

if __name__ == "__main__":
    # テスト：新構造での動作確認
    try:
        from thought_generator import generate_thought
        print(f"[*] Project Root: {BASE_DIR}")
        
        # テスト出力
        thought = generate_thought("深夜の公園のベンチ", context_type="teaser")
        print("\n🧠 Integrated Positive Prompt:\n", build_prompt(thought))
        print("\n🚫 Integrated Negative Prompt:\n", build_prompt(thought, negative=True))
    except ImportError as e:
        print(f"[-] ImportError: {e}. Check if thought_generator.py is in core/engines/")
    except Exception as e:
        print(f"[-] Execution Error: {e}")
