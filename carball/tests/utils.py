import os
import time
from typing import Callable, Tuple, Iterable

import numpy as np
from carball.decompile_replays import analyze_replay_file

REPLAYS_FOLDER = os.path.join(os.path.dirname(__file__), 'replays')


def get_multiple_answers(answers: Iterable[str]) -> Iterable[Tuple[any]]:
    return np.column_stack([get_specific_answers().get(key) for key in answers])


def run_tests_on_list(unit_test_func: Callable, replay_list=None, answers=None):
    if replay_list is None:
        replay_list = get_complex_replay_list()

    for index in range(len(replay_list)):
        replay_file = replay_list[index]
        print('running test on replay: ' + replay_file)
        answer = answers[index] if answers is not None and index < len(answers) else None
        run_replay(replay_file, unit_test_func, answer=answer)


def get_replay_path(replay_file):
    return os.path.join(REPLAYS_FOLDER, replay_file)


def run_replay(replay_file, unit_test_func: Callable, answer=None):
    """
    Runs the replay with the file downloaded locally then deletes the file.
    :param replay_file:
    :param unit_test_func:
    :param answer: data that can be passed to the replay to help judge it
    :return:
    """
    file = get_replay_path(replay_file)

    if answer is not None:
        unit_test_func(file, answer)
    else:
        unit_test_func(file)


def run_analysis_test_on_replay(unit_test_func: Callable, replay_list=None, answers=None, cache=None, calculate_intensive_events=False):
    """
    :param unit_test_func: Called with an AnalysisManager
    :param replay_list: list of replay urls
    :param calculate_intensive_events: Indicates if the test needs the replay to be analyzed against expensive-to-calculate events.
    :return:
    """

    def wrapper(replay_file_path, answer=None):
        start = time.time()
        if cache is not None and str(replay_file_path) in cache:
            analysis_manager = cache[str(replay_file_path)]
        else:
            analysis_manager = analyze_replay_file(replay_file_path, calculate_intensive_events=calculate_intensive_events)
        if cache is not None and time.time() - start > 10:
            cache[str(replay_file_path)] = analysis_manager
        if answer is not None:
            if isinstance(answer, (list, tuple, np.ndarray)):
                unit_test_func(analysis_manager, *answer)
            else:
                unit_test_func(analysis_manager, answer)
        else:
            unit_test_func(analysis_manager)

    run_tests_on_list(wrapper, replay_list, answers=answers)


def get_complex_replay_list():
    """
    For full replays that have crashed or failed to be converted
    :return:
    """
    return [
        'BOTS_JOINING_AND_LEAVING.replay',
        'BOTS_NO_POSITION.replay',
        'ZEROED_STATS.replay',
        'FAKE_BOTS_SkyBot.replay',
        'NEGATIVE_WASTED_COLLECTION.replay',
        'WASTED_BOOST_WHILE_SUPER_SONIC.replay',
        'OCE_RLCS_7_CARS.replay',
        'crossplatform_party.replay',
        'PARTY_LEADER_SYSTEM_ID_0.replay',
        'RL_1_66.replay',
        'CARRY.replay'
    ]


def get_raw_replays():
    """
    Partial replays for specific values.
    :return:
    """
    return {
        "0_JUMPS": ["0_JUMPS.replay"],
        "0_SAVES": ["0_SAVES.replay"],
        "1_AERIAL": ["1_AERIAL.replay"],
        "1_DEMO": ["1_DEMO.replay", "1_DEMO_1_63.replay"],
        "1_DOUBLE_JUMP": ["1_DOUBLE_JUMP.replay"],
        "1_EPIC_SAVE": ["1_EPIC_SAVE.replay"],
        "1_JUMP": ["1_JUMP.replay"],
        "1_NORMAL_SAVE_FROM_SHOT_TOWARD_POST": ["1_NORMAL_SAVE.replay"],

        # Boost
        "3_STEAL_ORANGE_0_STEAL_BLUE": ["3_STEALS.replay"],
        "12_BOOST_PAD_0_USED": ["12_BOOST_PAD_0_USED.replay"],
        "12_BOOST_PAD_45_USED": ["12_BOOST_PAD_45_USED.replay"],
        "100_BOOST_PAD_0_USED": ["100_BOOST_PAD_0_USED.replay"],
        "100_BOOST_PAD_100_USED": ["100_BOOST_PAD_100_USED.replay"],
        "NO_BOOST_PAD_0_USED": ["NO_BOOST_PAD_0_USED.replay"],
        "NO_BOOST_PAD_33_USED": ["NO_BOOST_PAD_33_USED.replay"],
        "12_AND_100_BOOST_PADS_0_USED": ["12_AND_100_BOOST_PADS_0_USED.replay", "1_100_1_12_0_BOOST_168.replay", "1_100_1_12_0_BOOST_168_ALT.replay"],
        "WASTED_BOOST_WHILE_SUPER_SONIC": ["WASTED_BOOST_WHILE_SUPER_SONIC.replay"],
        "CALCULATE_USED_BOOST_WITH_DEMO": ["CALCULATE_USED_BOOST_WITH_DEMO.replay"],
        "CALCULATE_USED_BOOST_DEMO_WITH_FLIPS": ["CALCULATE_USED_BOOST_DEMO_WITH_FLIPS.replay"],
        "MORE_THAN_100_BOOST": ["MORE_THAN_100_BOOST.replay"],
        "USE_BOOST_AFTER_GOAL": ["USE_BOOST_AFTER_GOAL.replay"],
        "FEATHERING_34x100_BO0ST_USED": ["FEATHERING_34_X_100_BOOSTS_USED.replay"],
        "6_BIG_25_SMALL": ["6_BIG_25_SMALL.replay"],

        # Kickoffs
        "STRAIGHT_KICKOFF_GOAL": ["Straight_Kickoff_Goal.replay"],
        "KICKOFF_NO_TOUCH": ["NO_KICKOFF.replay"],
        "LAST_KICKOFF_NO_TOUCH": ["LAST_KICKOFF_NO_TOUCH.replay"],
        "3_KICKOFFS": ["3_KICKOFFS_4_SHOTS.replay"],
        "5_DIVERSE_KICKOFFS": ["KICKOFF_TEST_1.replay"],
        "6_DIVERSE_KICKOFFS": ["KICKOFF_TEST_2.replay"],
        "NO_ONE_FOR_KICKOFF": ["NO_ONE_FOR_KICKOFF.replay"],
        "WEIRD_KICKOFFS": ["WEIRD_KICKOFFS.replay"],

        # hits
        "4_SHOTS": ["3_KICKOFFS_4_SHOTS.replay"],
        "KICKOFF_3_HITS": ["KICKOFF_3_HITS.replay"],
        "MID_AIR_PASS": ["MID_AIR_PASS_GOAL.replay"],
        "HIGH_AIR_PASS": ["HIGH_AIR_PASS_GOAL.replay"],
        "GROUND_PASS": ["GROUNDED_PASS_GOAL.replay"],
        "PINCH_GROUND": ["PINCH_GROUNDED_GOAL.replay"],
        "DEFAULT_3_ON_3_AROUND_58_HITS": ["DEFAULT_3_ON_3_AROUND_58_HITS.replay"],
        "1_CLEAR": ["1_CLEAR.replay"],
        "2_CLEARS": ["2_CLEARS.replay"],

        # KBM
        "1_MIN_KBM_1_MIN_XBO_CONTROLLER": ["1_MIN_KBM_1_MIN_XBO_CONTROLLER.replay"],
        "100_PERCENT_KBM": ["100_PERCENT_KBM.replay"],

        # camera controls
        "BALLCAM_ON_IN_CLOSE_AIR_ELSE_OFF": ["BALLCAM_ON_IN_CLOSE_AIR_ELSE_OFF.replay"],
        "BALLCAM_OFF_IN_CLOSE_AIR_ELSE_ON": ["BALLCAM_OFF_IN_CLOSE_AIR_ELSE_ON.replay"],
        "BALLCAM_MIXED": ["BALLCAM_MIXED.replay"],
        "BALLCAM_ON_AT_DRIBBLE_ELSE_OFF": ["BALLCAM_ON_AT_DRIBBLE_ELSE_OFF.replay"],
        "BALLCAM_OFF_AT_DRIBBLE_ELSE_ON": ["BALLCAM_OFF_AT_DRIBBLE_ELSE_ON.replay"],
        "BALLCAM_OFF_ALWAYS": ["BALLCAM_OFF_ALWAYS.replay"],
        "BALLCAM_ON_ALWAYS": ["BALLCAM_ON_ALWAYS.replay"],

        # Dribbles
        "SKYBOT_DRIBBLE_INFO": ["SKYBOT_DRIBBLE_INFO.replay"],
        "1_DRIBBLE": ["1_DRIBBLE.replay"],
        "3_DRIBBLE_2_FLICKS": ["3_DRIBBLE_2_FLICKS.replay"],

        # parties
        "PLAY_STATION_ONLY_PARTY": ['PLAY_STATION_ONLY_PARTY.replay'],
        # error cases
        "PLAYERNAME_BALL": ["PLAYERNAME_BALL.replay"],
        "PLAYERNAME_GAME": ["PLAYERNAME_GAME.replay"],
        "PLAYERNAME_TWO_PLAYERS_NAMED_SAME": ["PLAYERNAME_TWO_PLAYERS_NAMED_SAME.replay"],
        "PLAYERNAME_ZTTL": ["PLAYERNAME_ZTTL.replay"],
        "ISSUE_PLAYER_REJOIN": ["ISSUE_PLAYER_REJOIN.replay"],
        "OCE_RLCS_7_CARS": ["OCE_RLCS_7_CARS.replay"],
        "XBOX_PARTY": ["XBOX_PARTY.replay"],
        # error cases
        "UNICODE_ERROR": ["UnicodeEncodeError.replay"],
        "CROSSPLATFORM_PARTY_LEADER_ERROR": ["crossplatform_party.replay"],
        "PARTY_LEADER_SYSTEM_ID_0_ERROR": ['PARTY_LEADER_SYSTEM_ID_0.replay'],

        # rumble
        "RUMBLE_PRE_ITEM_GOALS": ["RUMBLE_PRE_ITEM_GOALS.replay"],
        "RUMBLE_ITEM_GOALS": ["RUMBLE_ITEM_GOALS.replay"],
        "RUMBLE_FREEZE_VS_SPIKE": ["RUMBLE_FREEZE_VS_SPIKE.replay"],
        "RUMBLE_HOLD_TIME": ["RUMBLE_HOLD_TIME.replay"],
        "RUMBLE_FULL": ["RUMBLE_FULL.replay"],
        "RUMBLE_ITEM_KICKOFF": ["RUMBLE_ITEM_KICKOFF.replay"],

        # dropshot
        "DROPSHOT_SINGLE_DAMAGE": ["DROPSHOT_SINGLE_DAMAGE.replay"],
        "DROPSHOT_DOUBLE_DAMAGE": ["DROPSHOT_DOUBLE_DAMAGE.replay"],
        "DROPSHOT_PHASE1_BALL": ["DROPSHOT_PHASE1_BALL.replay"],
        "DROPSHOT_PHASE2_BALL": ["DROPSHOT_PHASE2_BALL.replay"],
        "DROPSHOT_GOAL": ["DROPSHOT_GOAL.replay"],

        # ratteltrap errors
        "BROKEN_REPLAY": ["INVALID_FILE.replay"]
    }


def get_specific_replays():
    raw_map = get_raw_replays()
    return {
        # BOOSTS
        "0_BOOST_COLLECTED": raw_map["NO_BOOST_PAD_0_USED"] + raw_map["NO_BOOST_PAD_33_USED"] +
                             raw_map["KICKOFF_NO_TOUCH"],
        "1_SMALL_PAD": raw_map["12_BOOST_PAD_0_USED"] + raw_map["12_BOOST_PAD_45_USED"] +
                        raw_map['12_AND_100_BOOST_PADS_0_USED'],
        "1_LARGE_PAD": raw_map["100_BOOST_PAD_0_USED"] + raw_map["100_BOOST_PAD_100_USED"] +
                        raw_map['12_AND_100_BOOST_PADS_0_USED'],
        "0_BOOST_USED": raw_map["12_BOOST_PAD_0_USED"] + raw_map["100_BOOST_PAD_0_USED"] +
                        raw_map["NO_BOOST_PAD_0_USED"] + raw_map["KICKOFF_NO_TOUCH"] +
                        raw_map['12_AND_100_BOOST_PADS_0_USED'],
        "BOOST_USED": raw_map["12_BOOST_PAD_45_USED"] +
                      raw_map["100_BOOST_PAD_100_USED"] +
                      raw_map["NO_BOOST_PAD_33_USED"] +
                      raw_map["CALCULATE_USED_BOOST_WITH_DEMO"] +
                      raw_map["CALCULATE_USED_BOOST_DEMO_WITH_FLIPS"] +
                      raw_map["USE_BOOST_AFTER_GOAL"] +
                      raw_map["WASTED_BOOST_WHILE_SUPER_SONIC"],
        "BOOST_FEATHERED": raw_map["MORE_THAN_100_BOOST"] + raw_map["FEATHERING_34x100_BO0ST_USED"],
        "BOOST_WASTED_USAGE": raw_map["WASTED_BOOST_WHILE_SUPER_SONIC"],
        "BOOST_WASTED_COLLECTION": raw_map["MORE_THAN_100_BOOST"] + raw_map["12_AND_100_BOOST_PADS_0_USED"],
        # HITS
        "HITS": raw_map["4_SHOTS"] + raw_map["KICKOFF_3_HITS"] + raw_map["12_BOOST_PAD_45_USED"] +
                raw_map["MID_AIR_PASS"] + raw_map["HIGH_AIR_PASS"] + raw_map["GROUND_PASS"] +
                raw_map["1_NORMAL_SAVE_FROM_SHOT_TOWARD_POST"] + raw_map["1_EPIC_SAVE"] + raw_map["1_AERIAL"] +
                raw_map["DEFAULT_3_ON_3_AROUND_58_HITS"],
        # + raw_map["PINCH_GROUND"],  TODO: Fix pinches to create 2 hits 1 for each person on same frame
        "SHOTS": raw_map["4_SHOTS"] + raw_map["12_BOOST_PAD_45_USED"] +
                 raw_map["1_EPIC_SAVE"] + raw_map["1_NORMAL_SAVE_FROM_SHOT_TOWARD_POST"],
        "PASSES": raw_map["MID_AIR_PASS"] + raw_map["HIGH_AIR_PASS"] + raw_map["GROUND_PASS"],
        "AERIALS": raw_map["1_EPIC_SAVE"] + raw_map["1_AERIAL"] + raw_map["HIGH_AIR_PASS"] + raw_map["MID_AIR_PASS"],
        "CANT_CRASH": raw_map["UNICODE_ERROR"] + raw_map["PLAYERNAME_BALL"] + raw_map["PLAYERNAME_GAME"] +
                      raw_map["PLAYERNAME_TWO_PLAYERS_NAMED_SAME"] + raw_map["PLAYERNAME_ZTTL"] +
                      raw_map["ISSUE_PLAYER_REJOIN"] + raw_map["ISSUE_PLAYER_REJOIN"],
        "ZERO_DRIBBLE": raw_map["12_BOOST_PAD_45_USED"] + raw_map["KICKOFF_NO_TOUCH"],
        "DRIBBLES": raw_map["1_DRIBBLE"] + raw_map["3_DRIBBLE_2_FLICKS"] + raw_map["SKYBOT_DRIBBLE_INFO"],
        "SAVES": raw_map["1_EPIC_SAVE"] + raw_map["1_NORMAL_SAVE_FROM_SHOT_TOWARD_POST"],
        "OFFLINE": raw_map["3_KICKOFFS"],
        "BROKEN_REPLAYS": raw_map["BROKEN_REPLAY"],
        "CLEARS": raw_map['1_CLEAR'] + raw_map['2_CLEARS']
    }


def get_specific_answers():
    specific_replays = get_specific_replays()
    return {
        # Boost
        "0_BOOST_USED": [0] * len(specific_replays["0_BOOST_USED"]),
        "BOOST_USED": [45, 100, 33, 33.33 + 33.33 + 12.15, 33.33, 33.33, 0],
        "BOOST_WASTED_USAGE": [33.33],
        "BOOST_WASTED_COLLECTION": [[((31, 238), (255, 85))], [([255, 116],)], [([255, 116],)], [([255, 116],)]],
        "BOOST_FEATHERED": [100.0, 3490.0],
        # Hits
        "HITS": [4, 3, 1, 2, 9, 2, 4, 4, 4, 50],
        "SHOTS": [3, 0, 2, 1],
        "PASSES": [1, 1, 1],
        "AERIALS": [0, 1, 2, 0],
        "DRIBBLES": [1, 3, 49],
        "FLICKS": [0, 1, 0],
        "SAVES": [1, 0],
        "CLEARS": [1, 2],
    }


def assertNearlyEqual(case, a, b, percent=2.0, msg=None):
    if abs(a - b) > abs(percent / 100.0 * min(abs(a), abs(b))):
        if msg is None:
            case.fail("The given numbers %s and %s are not within %s percent of each other." % (a, b, percent))
        else:
            case.fail(msg)
