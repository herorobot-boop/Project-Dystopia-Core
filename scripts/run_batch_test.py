from prompt_engine import HK9_PromptEngine

# === テスト対象の scene_code 一覧 ===
scene_list = [
    "school_scene",
    "gym_scene",
    "cinema_scene",
    "still_scene"
]

# === タグごとの強度オーバーライド（任意） ===
default_overrides = {
    "F02": 0.35,
    "F01": 0.3,
    "F03": 0.4
}

# === 評価コメントのテンプレート（任意） ===
default_notes = "🔍 初回走行テスト"

# === 実行 ===
engine = HK9_PromptEngine()

for scene in scene_list:
    print(engine.generate_and_save(
        scene_code=scene,
        overrides=default_overrides,
        notes=default_notes
    ))
