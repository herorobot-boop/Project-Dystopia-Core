#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
import requests

MANDATORY_REPOS = [
    "https://github.com/ltdrdata/ComfyUI-Impact-Pack",
    "https://github.com/kijai/ComfyUI-segment-anything-2",
    "https://github.com/kijai/ComfyUI-KJNodes",
    "https://github.com/city96/ComfyUI-GGUF",
    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite",
    "https://github.com/roy-sau/ComfyUI-SendToDiscord",
]

CUSTOM_NODES = Path("/workspace/ComfyUI/custom_nodes")


def _pip_install(req: Path):
    cmd_break = [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "-r", str(req)]
    res = subprocess.run(cmd_break, check=False)
    if res.returncode != 0:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)], check=False)


def _resolve_branches(owner: str, repo: str) -> list[str]:
    branches: list[str] = []
    try:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", timeout=10)
        if r.status_code == 200:
            default_br = r.json().get("default_branch")
            if default_br:
                branches.append(default_br)
    except Exception:
        pass
    for b in ("main", "master"):
        if b not in branches:
            branches.append(b)
    return branches


def install_repo(repo_url: str) -> bool:
    clean_url = repo_url.rstrip("/")
    if clean_url.endswith(".git"):
        clean_url = clean_url[:-4]
    parts = clean_url.split("github.com/")[-1].split("/")
    if len(parts) < 2:
        print(f"[WARN] 不正なURL: {repo_url}")
        return False
    owner, repo_name = parts[0], parts[1]
    target = CUSTOM_NODES / repo_name
    if target.exists() and any(target.iterdir()):
        print(f"[Exist] {repo_name}")
        return True

    print(f"[Install] {repo_name} (tarball)")
    CUSTOM_NODES.mkdir(parents=True, exist_ok=True)
    branches = _resolve_branches(owner, repo_name)
    tmp_tgz = Path(f"/tmp/{repo_name}.tar.gz")

    installed = False
    for attempt in range(1, 4):
        for br in branches:
            shutil.rmtree(target, ignore_errors=True)
            tmp_tgz.unlink(missing_ok=True)
            target.mkdir(parents=True, exist_ok=True)
            tar_url = f"https://codeload.github.com/{owner}/{repo_name}/tar.gz/refs/heads/{br}"
            dl = subprocess.run(
                ["curl", "-fsSL", "--max-time", "180", tar_url, "-o", str(tmp_tgz)],
                check=False,
            )
            if dl.returncode == 0 and tmp_tgz.exists() and tmp_tgz.stat().st_size > 0:
                ext = subprocess.run(
                    ["tar", "-xzf", str(tmp_tgz), "-C", str(target), "--strip-components=1"],
                    check=False,
                )
                if ext.returncode == 0 and any(target.iterdir()):
                    tmp_tgz.unlink(missing_ok=True)
                    installed = True
                    break
        if installed:
            break
        shutil.rmtree(target, ignore_errors=True)
        tmp_tgz.unlink(missing_ok=True)
        if attempt < 3:
            print(f"[Retry {attempt}/3] {repo_name} 取得再試行...")
            time.sleep(5)

    if not installed:
        print(f"[WARN] 取得失敗: {repo_name}")
        return False

    req = target / "requirements.txt"
    if req.exists():
        _pip_install(req)
    print(f"[OK] {repo_name}")
    return True


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
