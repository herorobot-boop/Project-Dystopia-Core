import os

def scan_structure():
    print("--- Current Workspace Structure ---")
    for root, dirs, files in os.walk("/workspace"):
        level = root.replace("/workspace", "").count(os.sep)
        indent = " " * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        # ファイルが多い場合は5つまでに制限
        for f in files[:5]:
            print(f"{subindent}{f}")
    print("-----------------------------------")

if __name__ == "__main__":
    scan_structure()
