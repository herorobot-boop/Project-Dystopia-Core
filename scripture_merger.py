import json
import os

def merge_v2_patch():
    # パス設定
    master_path = 'config/dictionary/h_k9_dictionary_V2_Final.json'
    patch_path = 'patch.txt' # Geminiの出力をここに貼る
    
    with open(master_path, 'r', encoding='utf-8') as f:
        master = json.load(f)
        
    # パッチ（AIの出力）を読み込み
    with open(patch_path, 'r', encoding='utf-8') as f:
        patch_raw = f.read().strip()
        # 末尾のカンマ調整とオブジェクト化
        patch_data = json.loads("{" + patch_raw.rstrip(',') + "}")
        
    # 統合（V2_IDが重複した場合は上書き）
    master.update(patch_data)
    
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 聖典の更新完了。現在の総要素数: {len(master)} 件")

if __name__ == "__main__":
    merge_v2_patch()
