import json

def select_top_loras(registry_path="lora_registry.json", min_score=22):
    with open(registry_path, "r") as f:
        registry = json.load(f)

    selected = []
    for name, meta in registry.items():
        total = sum(meta["score"].values())
        if total >= min_score:
            selected.append((name, total))
    selected.sort(key=lambda x: x[1], reverse=True)
    return selected
