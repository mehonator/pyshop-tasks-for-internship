import unittest
from collections import namedtuple

import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)

from task_1_calc_score.task1_calc_score import get_score


OffsetEstimatesScores = namedtuple(
    "OffsetEstimatesScores", ["offset", "home", "away"]
)


class TestGetScoreMethod(unittest.TestCase):
    def setUp(self):
        self.GAME_STAMPS = [
            {"offset": 0, "score": {"away": 0, "home": 0}},
            {"offset": 3, "score": {"away": 0, "home": 0}},
            {"offset": 4, "score": {"away": 0, "home": 0}},
            {"offset": 5, "score": {"away": 0, "home": 0}},
            {"offset": 8, "score": {"away": 0, "home": 0}},
            {"offset": 2034, "score": {"away": 1, "home": 0}},
            {"offset": 2036, "score": {"away": 1, "home": 0}},
            {"offset": 2037, "score": {"away": 1, "home": 0}},
            {"offset": 2040, "score": {"away": 1, "home": 0}},
            {"offset": 2042, "score": {"away": 1, "home": 0}},
            {"offset": 10193, "score": {"away": 1, "home": 1}},
            {"offset": 10194, "score": {"away": 1, "home": 1}},
            {"offset": 10197, "score": {"away": 1, "home": 1}},
            {"offset": 10198, "score": {"away": 1, "home": 1}},
            {"offset": 19957, "score": {"away": 1, "home": 1}},
            {"offset": 19959, "score": {"away": 1, "home": 1}},
        ]

    def test_existing_offset(self):
        OFFSET_ESTIMATE_SCORES = [
            OffsetEstimatesScores(offset=0, home=0, away=0),
            OffsetEstimatesScores(offset=8, home=0, away=0),
            OffsetEstimatesScores(offset=2042, home=0, away=1),
            OffsetEstimatesScores(offset=10193, home=1, away=1),
            OffsetEstimatesScores(offset=19959, home=1, away=1),
        ]
        for offset_estimates_score in OFFSET_ESTIMATE_SCORES:
            with self.subTest(offset_estimates_score=offset_estimates_score):
                result = get_score(
                    self.GAME_STAMPS, offset_estimates_score.offset
                )
                estimate = (
                    offset_estimates_score.home,
                    offset_estimates_score.away,
                )
                self.assertEqual(result, estimate)

    def test_intermediate_offset(self):
        OFFSET_ESTIMATE_SCORES = [
            OffsetEstimatesScores(offset=1, home=0, away=0),
            OffsetEstimatesScores(offset=2040, home=0, away=1),
            OffsetEstimatesScores(offset=1000000, home=1, away=1),
        ]
        for offset_estimates_score in OFFSET_ESTIMATE_SCORES:
            with self.subTest(offset_estimates_score=offset_estimates_score):
                result = get_score(
                    self.GAME_STAMPS, offset_estimates_score.offset
                )
                estimate = (
                    offset_estimates_score.home,
                    offset_estimates_score.away,
                )
                self.assertEqual(result, estimate)

    def test_empty_stamps(self):
        empty_game_stamps = []
        with self.assertRaises(ValueError):
            get_score(empty_game_stamps, 1)

    def test_negative_stamps(self):
        with self.assertRaises(ValueError):
            get_score(self.GAME_STAMPS, -100)


if __name__ == "__main__":
    unittest.main()
