def ideology_filter(lora_name, required_tags, registry_path="lora_registry.json"):
    with open(registry_path, "r") as f:
        registry = json.load(f)
    tags = registry.get(lora_name, {}).get("tags", [])
    return all(tag in tags for tag in required_tags)
