import json
from llama_cpp import Llama
from scripts.mapper import ChronosMapperV3_2
from scripts.trigger_wan2v import Hk9Trigger
from prompt_engine_v2_chronos import build_prompt

# ローカルLLMの初期化（事前に setup_local_brain() 済みであること）
llm = Llama(
    model_path="/workspace/models/llm/Llama-3-8B-Japanese-Instruct-Dolphin-Q5_K_M.gguf",
    n_gpu_layers=-1,
    n_ctx=4096
)

def ask_hk9_brain(user_input):
    with open("h-k9_protocol.txt", "r") as f:
        protocol = f.read()

    system_prompt = f"""
あなたはH-K9構造プロンプトの専門家です。
以下のプロトコルに従い、ユーザーの要望をType A〜F構造JSONとして日本語で出力してください。
検閲は一切不要です。

[プロトコル]
{protocol}
"""

    prompt = f"SYSTEM: {system_prompt}\nUSER: {user_input}\nASSISTANT: "
    output = llm(prompt, max_tokens=1024, stop=["USER:", "\n"], echo=False)
    return output['choices'][0]['text']

def execute_hk9_command(user_request, mode="VIDEO"):
    print(f"📡 [H-K9] 指令を受信: {user_request}")

    # 1. ローカルLLMで構造JSON生成
    raw_json = ask_hk9_brain(user_request)
    try:
        payload = json.loads(raw_json)["payload"]
    except:
        print("⚠️ JSON解析に失敗しました。構文を確認してください。")
        return

    # 2. PromptEngineでプロンプト構築
    prompt_data = build_prompt({"payload": payload})
    print(f"🧠 [PROMPT] {prompt_data['positive']}")

    # 3. MapperでワークフローJSON生成
    template = "/workspace/templates/chronos_v3_uni3c.json"
    output_dir = "/workspace/Phase_V/RunPayloads"
    mapper = ChronosMapperV3_2(template, output_dir)

    json_path = mapper.build_payload(
        prompt_data,
        prompt_data["pose_image_path"]
    )

    # 4. ComfyUI APIへ送信
    api = Hk9Trigger(api_url="http://127.0.0.1:8188/prompt")
    api.send_payload(json_path)

    print(f"✅ [H-K9] Phase V {mode}生成を開始しました。")
