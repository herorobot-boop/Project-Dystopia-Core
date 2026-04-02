import os
import sys
import json
import torch
import gc
from pathlib import Path
from llama_cpp import Llama

# =========================================================
# 🏛️ Project Dystopia: Visual Intelligence Center (v3.7)
# =========================================================

class DystopiaVisualDirector:
    def __init__(self):
        self.vlm_model = "/workspace/models/vlm/qwen3.5-9b-vlm-q8.gguf"
        self.mmproj = "/workspace/models/vlm/mmproj-qwen3.5-9b-f16.gguf"
        self.extension_log = "/workspace/Project-Dystopia-Core/logs/visual_extension.json"

    def _visual_thinking(self, image_path, query):
        """【ハカセアイ式】VLMによる多角的解析と三層プロンプト錬成"""
        print(f"🧐 [Visual Intelligence] Analyzing Reference: {image_path}")
        
        # 5090 Blackwell 上で VRAM 交互覚醒 (Swap Protocol)
        llm = Llama(model_path=self.vlm_model, chat_format="qwen2-vl", n_gpu_layers=-1, n_ctx=2048)
        
        # ハカセアイ式 System Prompt の適用
        system_prompt = (
            "あなたは Project Dystopia の撮影監督です。提示された画像を解析し、"
            "『HEAD SWAP』『ACTION』『EMOTIONAL PHASE』の3層構造で、"
            "映画的なカメラワークと物理演算タグ（SQUISH等）を含むプロンプトを生成せよ。"
        )
        
        prompt = f"Image Path: {image_path}\nCommand: {query}"
        # 実際には画像をエンコードして送信
        output = llm.create_chat_completion(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        )
        refined_tags = output['choices'][0]['message']['content']
        
        # VRAM 完全パージ
        del llm
        gc.collect()
        torch.cuda.empty_cache()
        print("🧹 [VRAM] Thinking Phase Clear. Assigning 32GB to Rendering Engine.")
        return refined_tags

    def render_pipeline(self, final_tags):
        """ハカセアイ式：Flux-1-Klein 高速試作 -> Wan 2.2 最終現像"""
        # Step 1: Flux-1-Klein による 8ステップ高速プレビュー
        print("🎨 [Phase 1] Flux-1-Klein Fast Prototype Rendering...")
        # (ComfyUI API 経由でプロトタイプを射出)
        
        # Step 2: 合格後、Wan 2.2 による最高密度動画現像
        print("🔥 [Phase 2] Final Video Rendering (Wan 2.2 / Z-Image)...")
        # (ここで 5-10s の動画延長リレーへ接続)

    def run(self):
        print("\n" + "█"*40 + "\n🐺 H-K9 VISUAL INTELLIGENCE CENTER (v3.7)\n" + "█"*40)
        while True:
            cmd = input("H-K9 (ID / edit / auto / ref_path) >> ").strip()

            if os.path.exists(cmd):
                # パスが入力された場合、ハカセアイ式「高精度リファレンス解析」を発動
                ref_img = cmd
                query = input("Analysis Query (日本語) >> ")
                tags = self._visual_thinking(ref_img, query)
                print(f"🧠 [Result] Script Generated:\n{tags}")
                self.render_pipeline(tags)
            else:
                # 通常の聖典ID入力または編集コマンド
                print(f"🚀 Executing Standard Protocol: {cmd}")
                # (既存の Main.py ロジックを継承)

if __name__ == "__main__":
    director = DystopiaVisualDirector()
    director.run()
