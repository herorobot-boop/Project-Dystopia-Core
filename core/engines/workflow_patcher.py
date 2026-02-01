import json

def patch_workflow(base_json_path, output_json_path, denoise=0.35, model="zimage_6b.safetensors"):
    """
    既存のJSONを読み込み、Z-Image/5090環境用に数値を一括置換する。
    """
    with open(base_json_path, 'r') as f:
        workflow = json.load(f)

    # 全ノードをスキャンし、ターゲットの数値を書き換える
    for node_id, node in workflow.items():
        # サンプラーの設定変更
        if "denoise" in node.get("inputs", {}):
            node["inputs"]["denoise"] = denoise
        # モデルの変更
        if "ckpt_name" in node.get("inputs", {}):
            node["inputs"]["ckpt_name"] = model

    with open(output_json_path, 'w') as f:
        json.dump(workflow, f, indent=4)
    print(f"✅ Workflow patched: {output_json_path}")

# 使用例: LLMの指示を受けて実行
# patch_workflow("workflows/Type-A.json", "workflows/Type-A_ZImage_v3.json", denoise=0.4)
