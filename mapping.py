# core/mapping.py

import math

def apply_mapping(thought, workflow, mapping_config):
    context = {**thought}
    for key, rule in mapping_config.items():
        formula = rule["formula"]
        try:
            value = eval(formula, {"__builtins__": {}, "int": int, "round": round, "math": math}, context)
        except Exception as e:
            print(f"[Mapping Error] {key}: {e}")
            continue

        for node in workflow["nodes"]:
            if node["type"] == rule["target_node_type"]:
                fields = rule["target_field"].split(".")
                target = node
                for f in fields[:-1]:
                    target = target.setdefault(f, {})
                target[fields[-1]] = value
    return workflow
