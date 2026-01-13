import gradio as gr
from PromptEngine_v1 import PromptEngine  # 同じディレクトリに上のファイルがある前提

engine = PromptEngine()

def process(p_type, char, scene, style, extra):
    res = engine.generate(p_type, char, scene, style, extra)
    return res["positive"], res["negative"]

with gr.Blocks(title="Project Dystopia Cockpit") as demo:
    gr.Markdown("# 🧠 Project Dystopia: PromptEngine GUI")
    
    with gr.Row():
        t = gr.Radio(["A", "D", "E"], label="Workflow Type", value="A")
        c = gr.Textbox(label="Character (主役)", placeholder="1girl, detailed face...")
    
    with gr.Row():
        s = gr.Textbox(label="Scene (環境/行動)", placeholder="sitting on bed, sunlight...")
        st = gr.Textbox(label="Style (画風タグ)", placeholder="masterpiece, photorealistic...")
    
    e = gr.Textbox(label="Extra (フェチ/詳細/LoRAタグ)", placeholder="latex, [ANTI_MELT]...")
    gr.Markdown("💡 **Tip:** `[ANTI_MELT]`(破綻抑制), `[REAL_SKIN]`(質感向上), `[POSE_FIX]`(解剖学修正) 等が使用可能です。")
    
    btn = gr.Button("🔥 プロンプトを設計 (Forge Prompt)", variant="primary")
    
    with gr.Row():
        pos = gr.Code(label="🟢 Positive Prompt (ComfyUIにコピペ)")
        neg = gr.Code(label="🔴 Negative Prompt (ComfyUIにコピペ)")
    
    btn.click(process, inputs=[t, c, s, st, e], outputs=[pos, neg])

if __name__ == "__main__":
    # share=TrueでRunPod外のブラウザからもアクセス可能にする
    demo.launch(share=True)
