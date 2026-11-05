import math
import random
import json
from pathlib import Path

class MutationLab:
    def __init__(self, scores_file="/workspace/config/logic/mutation_scores.json", decay_factor=0.85, mutation_rate=0.20):
        self.scores_file = Path(scores_file)
        self.decay_factor = decay_factor
        self.mutation_rate = mutation_rate
        self.scores = self._load_scores()

    def _load_scores(self) -> dict:
        if self.scores_file.exists():
            with open(self.scores_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def apply_generational_decay(self):
        for tag in list(self.scores.keys()):
            self.scores[tag] *= self.decay_factor
            if self.scores[tag] < 0.1:
                del self.scores[tag]

    def select_mutated_tags(self, available_tags: list, top_k=3) -> list:
        self.apply_generational_decay()

        selected = []
        for tag in available_tags:
            if random.random() < self.mutation_rate:
                selected.append(tag)
            else:
                score = self.scores.get(tag, 1.0)
                if random.random() < (1.0 / (1.0 + math.exp(-score / 1.2))):
                    selected.append(tag)

        unique_tags = list(dict.fromkeys(selected))[:top_k]
        return unique_tags
