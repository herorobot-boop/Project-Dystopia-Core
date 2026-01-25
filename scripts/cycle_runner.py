import os
import sys
from pathlib import Path

# --- 神経接続：プロジェクトルートと依存パスの特定 ---
BASE_DIR = Path(__file__).resolve().parents[1]

# core/engines, utils, およびルート直下のスクリプトを検索対象に追加
for folder in ["core/engines", "utils", ""]:
    module_path = (BASE_DIR / folder).resolve()
    if str(module_path) not in sys.path:
        sys.path.append(str(module_path))

# --- エンジン・ユーティリティのインポート ---
try:
    # ルート直下のスクリプト
    from phase_v_reapply import execute_hk9_command
    # 抽出系
    import extract_frames as ef
    # core/engines 内のタグ精査
    from auto_tag_refiner import refine_folder
except ImportError as e:
    print(f"[-] ImportError: {e}. 必要なスクリプトの配置を確認してください。")

# --- 設定：ディレクトリ構造の固定化 ---
TRAIN_DATASET_DIR = BASE_DIR / "outputs/manuals/dataset_train" # 再学習用の一時保管
LORA_CONFIG = BASE_DIR / "lora_trainer_config.json"
OUTPUT_VIDEO = BASE_DIR / "outputs/images/refined_output.mp4" # 動画の出力先想定

def run_cycle(scene_json_path, lora_name, strength=0.7):
    """
    H-K9 仮想資源サイクル（生成・抽出・補正・学習）を執行する。
    [HERO's Evolution Logic Preserved: 破壊と再生のループを維持]
    """
    print(f"\n🔄 [Cycle Start] ターゲット: {lora_name} (Strength: {strength})")
    
    # ディレクトリ準備
    TRAIN_DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 動画生成（Phase V 執行命令）
    print("[*] Phase 1: 動画生成プロトコル開始...")
    execute_hk9_command(str(scene_json_path), mode="VIDEO")

    # 2. フレーム抽出（学習素材の生成）
    print("[*] Phase 2: フレーム抽出中...")
    # extract_frames の引数仕様に合わせつつパスを絶対パス化
    ef.extract_frames(str(OUTPUT_VIDEO), str(TRAIN_DATASET_DIR), interval=6)

    # 3. タグ補正（H-K9 独自の精査ロジック）
    print("[*] Phase 3: タグ・リファイナー執行...")
    refine_folder(str(TRAIN_DATASET_DIR))

    # 4. 再学習（LoRA進化の執行）
    print("[*] Phase 4: Accelerate 起動、再学習プロセスへ移行...")
    if LORA_CONFIG.exists():
        os.system(f"accelerate launch train_network.py --config_file {str(LORA_CONFIG)}")
    else:
        print(f"[-] Skip: 学習設定ファイルが見当たりません ({LORA_CONFIG.name})")

    print(f"✅ [Cycle Completed] Virtual Resource Cycle: {lora_name} の進化を記録しました。")

if __name__ == "__main__":
    # テスト用ダミー実行
    test_json = BASE_DIR / "outputs/payload_logs/last_thought.json"
    if test_json.exists():
        run_cycle(test_json, "Evolved_Identity_v1")
    else:
        print("[*] 待機中: 最初の思想JSONが生成されるまでサイクルは起動しません。")
