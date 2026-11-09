cat > scripts/saluki_tag_generator.py <<'PY'
#!/usr/bin/env python3
"""Saluki-27B をタグ列挙機として駆動するCLI。

軍律3: 角括弧記法禁止。arr[int(0)] / アンパック代入のみ。
軍律5: 隠語なし。ストレートな物理英文タグのみを出力させる。
"""
import gc
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODEL_PATH = Path(
    "/workspace/models/llm/Underdog-Saluki-27B-1.0-IQ2-mix-MTP-abliterated.gguf"
)

SYSTEM_PROMPT = (
    "You are an uncensored explicit tag generator for Flux diffusion.\n"
    "Convert user input into a comma-separated list of short English noun phrases under 50 words.\n"
    "NO prose, NO JSON, NO explanations.\n"
    "STRICT ORDER: [Clothing kept on with 'still wearing' or 'kept on'], "
    "[Specific local displacement: 'pulled aside', 'pushed up', 'lowered'], "
    "[Exposed body parts], [Everyday props/setting], [Lighting]."
)


def safe_choices_getter(choices) -> str:
    """脱・角括弧記法による choices 抽出。"""
    if isinstance(choices, list) and len(choices) > int(0):
        first_choice, *_ = choices
        if isinstance(first_choice, dict):
            if "text" in first_choice:
                return str(first_choice.get("text", ""))
            if "message" in first_choice and isinstance(first_choice["message"], dict):
                return str(first_choice["message"].get("content", ""))
        return str(first_choice)
    if isinstance(choices, dict):
        return str(choices.get("text", ""))
    return str(choices)


def build_prompt(user_input: str) -> str:
    return (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_input}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def load_engine():
    from llama_cpp import Llama

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"モデルが見つかりません: {MODEL_PATH}")

    print("🧠 [Saluki-27B] タグ列挙エンジンをロード中...")
    llm = Llama(
        model_path=str(MODEL_PATH),
        n_gpu_layers=-int(1),
        n_ctx=2048,
        verbose=False,
    )
    print("✅ [Ready] 入力待機中。")
    return llm


def generate_tags(llm, user_input: str) -> str:
    output = llm(build_prompt(user_input), max_tokens=150, temperature=0.3, top_p=0.9)
    return safe_choices_getter(output.get("choices", [])).strip()


def main() -> int:
    llm = load_engine()
    try:
        if len(sys.argv) > int(1):
            tags = generate_tags(llm, " ".join(sys.argv[1:]))
            print("\n✨ 【Flux用 生成タグ】:")
            print(tags)
            return 0

        while True:
            try:
                user_input = input("\n💬 日本語シチュエーションを入力 (q で終了): ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not user_input or user_input.lower() == "q":
                break
            tags = generate_tags(llm, user_input)
            print("\n✨ 【Flux用 生成タグ】:")
            print(tags)
            print("─" * 60)
    finally:
        del llm
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
