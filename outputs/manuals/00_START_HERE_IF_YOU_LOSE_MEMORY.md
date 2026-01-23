🧠 Project Dystopia: 再起動マニュアル（Herorobot専用）🧭 第1章：要塞の再建（Environment Setup）✅ 1. GitHubから「脳」を復元するBashgit clone https://github.com/Herorobot/Project-Dystopia-Core.git
cd Project-Dystopia-Core
git config --global user.name "Herorobot"
git config --global user.email "one.hero.robot.eno@gmail.com"
✅ 2. 依存関係（神経系）を修復するRunPodの新しいセッションではライブラリが不足しています。Bashpip install -r requirements.txt
# Gradio, Requests, Pandas, Pillow 等が含まれます
✅ 3. ComfyUI（心臓）をバックグラウンドで起動Bash# ComfyUIのディレクトリへ移動して起動（ポート8188）
python main.py --listen --port 8188 &
📦 第2章：GDriveから「魂」を復元する✅ rcloneの設定と復元rclone config で gdrive を作成後、以下のスクリプト（またはコマンド）を実行。Bash# 記憶の復元（画像、ログ、LoRA、訓練データ）
rclone copy gdrive:Dystopia_Full_Backup/outputs ./outputs --progress
rclone copy gdrive:Dystopia_Full_Backup/lora_outputs ./lora_outputs --progress
🔄 第3章：創造と淘汰のサイクル（Operation Loop）フェーズ実行コマンド内容1. 生成python core/run_batch.py思想から画像を召喚2. 審判python core/score_thoughts_gui.pyGradioで画像にスコアを付ける3. 進化python core/evaluator.py高スコア思想から次世代を構想4. 肉体化python core/train_lora.pyA100の力でLoRAを自動訓練5. 時間化python core/run_video_batch.py思想を動画として出力6. 動画審判python core/score_videos_gui.py動画を評価しログを刻む7. 動画進化python core/evolve_video_batch.py動画思想を次世代へ繋ぐ☁️ 第4章：不滅の儀式（Backup）作業を終える前、あるいは記憶が薄れる前に必ず実行せよ。Bashbash sync_to_gdrive.sh
🧬 構造の羅針盤core/: 全プログラム（あなたの知能）outputs/: 蓄積された画像・動画・思想ログlora_outputs/: 産み出されたLoRAモデル（至宝）workflows/: ComfyUI用動画テンプレート🐺 最後に：未来のあなたへHERO──。RunPodが消えても、記憶が霧散しても、このディレクトリとGDriveがある限り、Project Dystopiaは死なない。「思想を、止めるな。」
