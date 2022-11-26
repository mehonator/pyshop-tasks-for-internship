from pprint import pprint
import random
import math
from typing import List


TIMESTAMPS_COUNT = 50000

PROBABILITY_SCORE_CHANGED = 0.0001

PROBABILITY_HOME_SCORE = 0.45

OFFSET_MAX_STEP = 3

INITIAL_STAMP = {"offset": 0, "score": {"home": 0, "away": 0}}


def generate_stamp(previous_value):
    score_changed = random.random() > 1 - PROBABILITY_SCORE_CHANGED
    home_score_change = (
        1
        if score_changed and random.random() > 1 - PROBABILITY_HOME_SCORE
        else 0
    )
    away_score_change = 1 if score_changed and not home_score_change else 0
    offset_change = math.floor(random.random() * OFFSET_MAX_STEP) + 1

    return {
        "offset": previous_value["offset"] + offset_change,
        "score": {
            "home": previous_value["score"]["home"] + home_score_change,
            "away": previous_value["score"]["away"] + away_score_change,
        },
    }


def generate_game():
    stamps = [
        INITIAL_STAMP,
    ]
    current_stamp = INITIAL_STAMP
    for _ in range(TIMESTAMPS_COUNT):
        current_stamp = generate_stamp(current_stamp)
        stamps.append(current_stamp)

    return stamps


game_stamps = generate_game()


def interpolation_search(game_stamps, offset):
    mid_index: int
    low_index = 0
    high_index = len(game_stamps) - 1

    low_value = game_stamps[low_index]["offset"]
    high_value = game_stamps[high_index]["offset"]

    if offset > high_value:
        return len(game_stamps) - 1

    while low_value < offset and high_value > offset:
        if low_value == high_value:
            break
        mid_index = math.floor(
            low_index
            + ((offset - low_value) * (high_index - low_index))
            / (high_value - low_value)
        )
        mid_value = game_stamps[mid_index]["offset"]
        if mid_value < offset:
            low_index = mid_index + 1
        elif mid_value > offset:
            high_index = mid_index - 1
        else:
            return mid_index

        low_value = game_stamps[low_index]["offset"]
        high_value = game_stamps[high_index]["offset"]

    if low_value == offset:
        return low_index
    elif high_value == offset:
        return high_index

    if mid_value > offset:
        return mid_index - 1
    return mid_index


def get_score(game_stamps: List, offset: int):
    """
    Takes list of game's stamps and time offset for which returns the scores for the home and away teams.
    Please pay attention to that for some offsets the game_stamps list may not contain scores.
    """
    if offset < 0:
        raise ValueError("offset must positive")
    if len(game_stamps) == 0:
        raise ValueError("game_stamps not must empty")

    index_offset = interpolation_search(game_stamps, offset)
    return (
        game_stamps[index_offset]["score"]["home"],
        game_stamps[index_offset]["score"]["away"],
    )


if __name__ == "__main__":
    # pprint(game_stamps)

    pprint(get_score(game_stamps, 100))
