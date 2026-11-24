import unittest
from quiz_logic import QuizLogic

class QuizTests(unittest.TestCase):
    def test_sequential(self):
        q=QuizLogic(range(1,221))
        self.assertEqual([q.next_question() for _ in range(220)],list(range(1,221)))
        self.assertFalse(q.still_has_questions())
        self.assertIsNone(q.next_question())
    def test_shuffle_unique_and_finite(self):
        q=QuizLogic(range(1,221),shuffle=True,seed=10)
        observed=[q.next_question() for _ in range(220)]
        self.assertEqual(len(set(observed)),220)
        self.assertEqual(set(observed),set(range(1,221)))
        self.assertIsNone(q.next_question())
    def test_reset(self):
        q=QuizLogic([1,2,3]);q.next_question();q.reset()
        self.assertEqual(q.progress,(0,3))
        self.assertEqual(q.next_question(),1)

if __name__ == '__main__': unittest.main()

class NavigationTests(unittest.TestCase):
    def test_previous_and_forward(self):
        q = QuizLogic([1, 2, 3])
        self.assertIsNone(q.previous_question())
        self.assertEqual(q.next_question(), 1)
        self.assertFalse(q.has_previous())
        self.assertEqual(q.next_question(), 2)
        self.assertEqual(q.previous_question(), 1)
        self.assertEqual(q.next_question(), 2)
        self.assertEqual(q.next_question(), 3)
        self.assertIsNone(q.next_question())
        self.assertEqual(q.current_question, 3)
        self.assertEqual(q.previous_question(), 2)

    def test_shuffle_backtracks_same_order(self):
        q = QuizLogic(range(1, 221), shuffle=True, seed=42)
        first = [q.next_question() for _ in range(10)]
        self.assertEqual(q.previous_question(), first[-2])
        self.assertEqual(q.next_question(), first[-1])
