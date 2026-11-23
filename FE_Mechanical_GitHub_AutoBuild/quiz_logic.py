"""Finite, non-repeating question scheduler with backwards navigation."""
import random

class QuizLogic:
    def __init__(self, question_ids=range(1, 221), shuffle=False, seed=None):
        self.question_ids = list(question_ids)
        if len(set(self.question_ids)) != len(self.question_ids):
            raise ValueError("Duplicate question IDs")
        self._rng = random.Random(seed)
        self.shuffle = shuffle
        self.reset()

    def reset(self):
        self.order = self.question_ids.copy()
        if self.shuffle:
            self._rng.shuffle(self.order)
        self.index = -1
        self.current_question = None

    def still_has_questions(self):
        return self.index + 1 < len(self.order)

    def has_previous(self):
        return self.index > 0

    def next_question(self):
        if not self.still_has_questions():
            return None
        self.index += 1
        self.current_question = self.order[self.index]
        return self.current_question

    def previous_question(self):
        if not self.has_previous():
            return None
        self.index -= 1
        self.current_question = self.order[self.index]
        return self.current_question

    def show_answer(self):
        return self.current_question

    @property
    def progress(self):
        return max(0, self.index + 1), len(self.order)
