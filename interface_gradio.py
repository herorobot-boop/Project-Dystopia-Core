import gradio as gr
from PromptEngine_v1 import PromptEngine

engine = PromptEngine()

def process(p_type, char, scene, style, extra):
    res = engine.generate(p_type, char, scene, style, extra)
    return res["positive"], res["negative"]

with gr.Blocks(title="Project Dystopia Cockpit") as demo:
    gr.Markdown("# 🧠 Project Dystopia: PromptEngine GUI")
    with gr.Row():
        t = gr.Radio(["A", "D", "E"], label="Workflow Type", value="A")
        c = gr.Textbox(label="Character (主役)")
    s = gr.Textbox(label="Scene (環境/行動)")
    st = gr.Textbox(label="Style (画風タグ)")
    e = gr.Textbox(label="Extra (フェチ/詳細)")
    
    pos = gr.Code(label="🟢 Positive Prompt")
    neg = gr.Code(label="🔴 Negative Prompt")
    
    btn = gr.Button("🔥 プロンプトを設計", variant="primary")
    btn.click(process, inputs=[t, c, s, st, e], outputs=[pos, neg])

if __name__ == "__main__":
    demo.launch(share=True)