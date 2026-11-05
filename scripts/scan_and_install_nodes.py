import os
import json
import subprocess
import requests
from pathlib import Path

def auto_install_missing_nodes(workflow_json_path: str):
    with open(workflow_json_path, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    class_types = set()
    if "nodes" in wf and isinstance(wf["nodes"], list):
        for node in wf["nodes"]:
            if "type" in node:
                class_types.add(node["type"])
    else:
        for node_id, node_info in wf.items():
            if isinstance(node_info, dict) and "class_type" in node_info:
                class_types.add(node_info["class_type"])

    repo_owner = "ltdrdata"
    map_url = f"https://raw.githubusercontent.com/{repo_owner}/ComfyUI-Manager/main/extension-node-map.json"

    try:
        node_map_data = requests.get(map_url, timeout=10).json()
    except Exception as e:
        print(f"⚠️ [Node Installer] extension-node-map.json 取得エラー: {e}")
        return

    custom_nodes_dir = Path("/workspace/ComfyUI/custom_nodes")

    for class_name in class_types:
        if class_name in node_map_data:
            entry = node_map_data[class_name]
            if isinstance(entry, list) and len(entry) > int(0):
                first_elem, *_ = entry
                repo_url = None
                if isinstance(first_elem, list) and len(first_elem) > int(0):
                    repo_url, *_ = first_elem
                elif isinstance(first_elem, str):
                    repo_url = first_elem

                if repo_url and repo_url.startswith("http"):
                    repo_name = repo_url.rstrip("/").split("/")[-int(1)].replace(".git", "")
                    target_path = custom_nodes_dir / repo_name
                    if not target_path.exists():
                        print(f"📦 [Auto-Install] クラス 『{class_name}』 のリポジトリを自動クローン: {repo_name}")
                        subprocess.run(f"git clone {repo_url} '{target_path}'", shell=True, check=True)
                        req_file = target_path / "requirements.txt"
                        if req_file.exists():
                            subprocess.run(f"pip install -r '{req_file}'", shell=True)

if __name__ == "__main__":
    auto_install_missing_nodes("/workspace/Project-Dystopia-Core/workflows/wan22_fun_camera_api.json")
