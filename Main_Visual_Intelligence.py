import os
import sys
import json
import torch
import gc
from pathlib import Path
from llama_cpp import Llama

# 内部エンジンのロード
sys.path.append(str(Path(__file__).resolve().parent / "core/engines"))
from thought_translator import ThoughtTranslator
from comfy_api_bridge import ComfyAPIBridge

class DystopiaVisualDirector:
    def __init__(self):
        self.vlm_model = "/workspace/models/vlm/qwen3.5-9b-vlm-q8.gguf"
        self.translator = ThoughtTranslator()
        self.bridge = ComfyAPIBridge()

    def _visual_thinking(self, image_path, mission_id):
        """【ハカセアイ式】VLMによる多角的解析とプロンプト錬成"""
        print(f"🧐 [Visual Intelligence] Analyzing context for: {mission_id}")
        
        # 35Bの脳を呼び出す前に9Bの眼で先行解析 (VRAM節約)
        llm = Llama(model_path=self.vlm_model, n_gpu_layers=-1, n_ctx=2048, jinja=True)
        
        # 聖典からの日本語指令を取得
        sacred_text = self.translator.translate(mission_id)
        
        # ハカセアイ式System Promptの適用 [ID:041]
        system_msg = (
            "あなたはProject Dystopiaの撮影監督です。リファレンス画像を解析し、"
            "聖典の指示に基づいた『HEAD SWAP』『ACTION』『EMOTIONAL PHASE』のプロンプトを生成せよ。"
        )
        
        # 実際にはここで画像を読み込んでVLM推論
        prompt = f"IMAGE_REF: {image_path}, INSTRUCTION: {sacred_text}"
        output = llm.create_chat_completion(messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}])
        
        refined_prompt = output['choices']['message']['content']
        
        # VRAMパージ (Swap Protocol)
        del llm
        gc.collect()
        torch.cuda.empty_cache()
        return refined_prompt

    def execute_mission(self, mission_id, ref_image=None):
        print(f"\n🚀 MISSION START: {mission_id}")
        
        # 1. 視覚的思考フェーズ
        if ref_image:
            final_prompt = self._visual_thinking(ref_image, mission_id)
        else:
            # 画像がない場合は従来の聖典翻訳
            final_prompt = self.translator.translate(mission_id)

        print(f"🧠 [Result] Visual Script Generated: {final_prompt[:100]}...")

        # 2. Flux-1-Klein による高速プレビュー (8 steps) [ID:041]
        print("🎨 [Phase 2] Fast Preview with Flux-1-Klein...")
        preview_id = self.bridge.send_to_factory(final_prompt, mode="preview")
        
        # 3. Z-Image / Wan 2.2 による最終現像
        print("🔥 [Phase 3] Final High-Precision Rendering...")
        # プレビューで合格なら本番へ (実際には自動判定)
        self.bridge.send_to_factory(final_prompt, mode="final")

if __name__ == "__main__":
    director = DystopiaVisualDirector()
    while True:
        cmd = input("H-K9 Visual >> ").strip()
        if cmd.startswith("V2_"):
            # 画像パスを引数として受け取ることも可能
            director.execute_mission(cmd)
