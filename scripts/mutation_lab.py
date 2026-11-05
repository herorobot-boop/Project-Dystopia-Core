import os
import math
import random
import json
from pathlib import Path

class MutationLab:
    def __init__(self, scores_file="/workspace/config/logic/mutation_scores.json", decay_factor=0.85, mutation_rate=0.20):
        self.scores_file = Path(scores_file)
        self.scores_file.parent.mkdir(parents=True, exist_ok=True)
        self.decay_factor = decay_factor
        self.mutation_rate = mutation_rate
        self.scores = self._load_scores()

    def _load_scores(self) -> dict:
        if self.scores_file.exists():
            try:
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_scores(self):
        with open(self.scores_file, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)

    def apply_generational_decay(self):
        """全スコアに指数減衰を適用し、陳腐化したタグを自動忘却"""
        tags_to_delete = []
        for tag, score in self.scores.items():
            new_score = score * self.decay_factor
            if new_score < 0.10:
                tags_to_delete.append(tag)
            else:
                self.scores[tag] = round(new_score, 4)

        for tag in tags_to_delete:
            del self.scores[tag]
        self._save_scores()

    def record_feedback(self, successful_tags: list, reward: float = 1.0):
        """合格したタグに対して正の報酬を加算"""
        for tag in successful_tags:
            current = self.scores.get(tag, 1.0)
            self.scores[tag] = round(current + reward, 4)
        self._save_scores()

    def select_mutated_tags(self, candidate_tags: list, top_k: int = 3) -> list:
        """変異率(20%) ＋ Softmax温度サンプリング(T=1.2) によるタグ選定"""
        self.apply_generational_decay()

        selected = []
        for tag in candidate_tags:
            # 20%の確率でランダム強制変異（モード崩壊の物理遮断）
            if random.random() < self.mutation_rate:
                selected.append(tag)
            else:
                score = self.scores.get(tag, 1.0)
                # T = 1.2 Softmax 確率計算
                prob = 1.0 / (1.0 + math.exp(-score / 1.2))
                if random.random() < prob:
                    selected.append(tag)

        # 重複排除および上位 top_k へのクランプ
        unique_tags = list(dict.fromkeys(selected))
        if not unique_tags and candidate_tags:
            unique_tags = random.sample(candidate_tags, min(top_k, len(candidate_tags)))

        final_selection = unique_tags[:top_k]
        print(f"🧬 [Mutation Lab] 変異選定タグ (top {top_k}): {final_selection}")
        return final_selection

if __name__ == "__main__":
    lab = MutationLab()
    test_pool = [
        "high fabric tension", "seam stress at waistband", "subsurface scattering",
        "cold fluorescent key", "extreme specular highlight", "fluid viscosity reflection"
    ]
    chosen = lab.select_mutated_tags(test_pool, top_k=3)
    lab.record_feedback(chosen, reward=1.5)
