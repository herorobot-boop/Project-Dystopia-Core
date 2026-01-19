import os
import json
import re
from datetime import datetime

class ChronosMapperV3_2:
    def __init__(self, template_path="structure_tags.json", output_dir="mapped/"):
        self.template_path = template_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.tag_db = self._load_tag_db()

    def _load_tag_db(self):
        with open(self.template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract_tags(self, text):
        tag_pattern = r"[A-F]\d{2}"
        return sorted(set(re.findall(tag_pattern, text)))

    def build_payload(self, llm_output, pose_path=None):
        # LLM出力がJSONならそのまま、自然文ならタグ抽出
        if isinstance(llm_output, dict):
            tags = llm_output.get("tags", [])
            description = llm_output.get("description", "")
        else:
            tags = self.extract_tags(llm_output)
            description = llm_output.strip().split("\n")[0]

        if not tags:
            raise ValueError("構造タグが見つかりませんでした")

        # scene_codeを生成（例：scene_A01_C01_D02）
        scene_code = "scene_" + "_".join(tags)

        payload = {
            "scene_code": scene_code,
            "tags": tags,
            "description": description,
            "pose_path": pose_path or f"/workspace/Phase_V/Inputs/pose_{tags[0]}.png"
        }

        # 保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(self.output_dir, f"{scene_code}_{timestamp}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"✅ 構造タグ抽出完了 → {out_path}")
        return payload
