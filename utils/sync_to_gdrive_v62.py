import os
import subprocess
from datetime import datetime

# 最終確定ルールに基づくパス
PROJECT_DIR = "/workspace/Project-Dystopia-Core"
REMOTE_PATH = "gdrive:Dystopia_Full_Backup"

def backup_execution():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    print(f"📦 Starting Backup Phase: {timestamp}")
    
    # 1. 脳（コードと設定）のバックアップ
    # config配下の聖典を最優先
    subprocess.run(f'rclone copy {PROJECT_DIR} {REMOTE_PATH}/code/{timestamp} --include "/core/**" --include "/config/**" --progress', shell=True)
    
    # 2. 記憶（成果物）の同期
    # 最終ルール: 空ディレクトリも保持し、構造を壊さない
    subprocess.run(f'rclone copy {PROJECT_DIR}/outputs {REMOTE_PATH}/outputs --progress --create-empty-src-dirs', shell=True)

if __name__ == "__main__":
    backup_execution()
