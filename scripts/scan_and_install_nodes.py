#!/usr/bin/env python3
import json
import subprocess
import requests
from pathlib import Path

MANDATORY_REPOS = [
    "https://github.com/ltdrdata/ComfyUI-Impact-Pack",
    "https://github.com/kijai/ComfyUI-segment-anything-2",
    "https://github.com/kijai/ComfyUI-KJNodes",
    "https://github.com/city96/ComfyUI-GGUF",
    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite",
    "https://github.com/roy-sau/ComfyUI-SendToDiscord",
]

CUSTOM_NODES = Path("/workspace/ComfyUI/custom_nodes")


def install_repo(repo_url: str):
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    target = CUSTOM_NODES / repo_name
    if target.exists():
        print(f"[Exist] {repo_name}")
        return
    print(f"[Install] {repo_name}")
    subprocess.run(f"git clone {repo_url} '{target}'", shell=True, check=True)
    req = target / "requirements.txt"
    if req.exists():
        subprocess.run(f"pip install -r '{req}'", shell=True)


def auto_install_from_workflow(workflow_json_path: str):
    for url in MANDATORY_REPOS:
        install_repo(url)

    wf_path = Path(workflow_json_path)
    if not wf_path.exists():
        print("[Node Installer] ワークフロー未配置。必須ノードのみ導入して待機")
        return

    with open(wf_path, "r", encoding="utf-8") as f:
        wf = json.load(f)

    class_types = set()
    if "nodes" in wf and isinstance(wf["nodes"], list):
        for node in wf["nodes"]:
            if "type" in node:
                class_types.add(node["type"])
    else:
        for node_info in wf.values():
            if isinstance(node_info, dict) and "class_type" in node_info:
                class_types.add(node_info["class_type"])

    try:
        node_map = requests.get(
            "https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/extension-node-map.json",
            timeout=10,
        ).json()
    except Exception as e:
        print(f"[Node Installer] node-map 取得失敗: {e}")
        return

    for class_name in class_types:
        if class_name not in node_map:
            continue
        entry, *_ = node_map[class_name]
        if not isinstance(entry, list) or not entry:
            continue
        repo_url, *_ = entry
        if isinstance(repo_url, str) and repo_url.startswith("http"):
            install_repo(repo_url)


if __name__ == "__main__":
    auto_install_from_workflow("/workspace/Project-Dystopia-Core/workflows/wan22_i2v_api.json")
