import os
import tempfile
from typing import Callable

import requests
from carball.decompile_replays import analyze_replay_file


def download_replay_discord(url):
    file = requests.get(url, stream=True)
    replay = file.raw.data
    return replay


def save_locally(replay_object):
    fd, file_path = tempfile.mkstemp()
    with open(file_path, 'wb') as f:
        f.write(replay_object)

    os.close(fd)
    return file_path


def run_tests_on_list(unit_test_func: Callable, replay_list=None, answers=None):
    if replay_list is None:
        replay_list = get_complex_replay_list()

    for index in range(len(replay_list)):
        replay_url = replay_list[index]
        print('running test on replay: ' + replay_url[replay_url.rfind('/') + 1:])
        answer = answers[index] if answers is not None and index < len(answers) else None
        run_replay(replay_url, unit_test_func, answer=answer)


def run_replay(url, unit_test_func: Callable, answer=None):
    """
    Runs the replay with the file downloaded locally then deletes the file.
    :param url:
    :param unit_test_func:
    :param answer: data that can be passed to the replay to help judge it
    :return:
    """

    replay = download_replay_discord(url)
    file = save_locally(replay)

    fd, file_path = tempfile.mkstemp()
    os.close(fd)
    if answer is not None:
        unit_test_func(file, file_path, answer)
    else:
        unit_test_func(file, file_path)
    os.remove(file)
    os.remove(file_path)


def run_analysis_test_on_replay(unit_test_func: Callable, replay_list=None, answers=None):
    """
    :param unit_test_func: Called with an AnalysisManager
    :param replay_list: list of replay urls
    :return:
    """

    def wrapper(replay_file_path, json_file_path, answer=None):
        analysis_manager = analyze_replay_file(replay_file_path)
        if answer is not None:
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
        'https://cdn.discordapp.com/attachments/493849514680254468/496153554977816576/BOTS_JOINING_AND_LEAVING.replay',
        'https://cdn.discordapp.com/attachments/493849514680254468/496153569981104129/BOTS_NO_POSITION.replay',
        'https://cdn.discordapp.com/attachments/493849514680254468/496153605074845734/ZEROED_STATS.replay',
        'https://cdn.discordapp.com/attachments/493849514680254468/496180938968137749/FAKE_BOTS_SkyBot.replay',
        'https://cdn.discordapp.com/attachments/493849514680254468/497149910999891969/NEGATIVE_WASTED_COLLECTION.replay',
        'https://cdn.discordapp.com/attachments/493849514680254468/497191273619259393/WASTED_BOOST_WHILE_SUPER_SONIC.replay',
        'https://cdn.discordapp.com/attachments/493849514680254468/501630263881760798/OCE_RLCS_7_CARS.replay'
    ]


def get_raw_replays():
    """
    Partial replays for specific values.
    :return:
    """
    return {
        "0_JUMPS": ["https://cdn.discordapp.com/attachments/493849514680254468/495735116895748096/0_JUMPS.replay"],
        "0_SAVES": ["https://cdn.discordapp.com/attachments/493849514680254468/495735137133264897/0_SAVES.replay"],
        "1_AERIAL": ["https://cdn.discordapp.com/attachments/493849514680254468/495735149133168651/1_AERIAL.replay"],
        "1_DEMO": ["https://cdn.discordapp.com/attachments/493849514680254468/495735163117109249/1_DEMO.replay"],
        "1_DOUBLE_JUMP": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735176761049103/1_DOUBLE_JUMP.replay"],
        "1_EPIC_SAVE": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735191537713153/1_EPIC_SAVE.replay"],
        "1_JUMP": ["https://cdn.discordapp.com/attachments/493849514680254468/495735203323576321/1_JUMP.replay"],
        "1_NORMAL_SAVE": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735215767945234/1_NORMAL_SAVE.replay"],

        # Boost
        "12_BOOST_PAD_0_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735228422291456/12_BOOST_PAD_0_USED.replay"],
        "12_BOOST_PAD_45_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735240321662986/12_BOOST_PAD_45_USED.replay"],
        "100_BOOST_PAD_0_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735252233224193/100_BOOST_PAD_0_USED.replay"],
        "100_BOOST_PAD_100_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735264262488065/100_BOOST_PAD_100_USED.replay"],
        "NO_BOOST_PAD_0_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735276338020372/NO_BOOST_PAD_0_USED.replay"],
        "NO_BOOST_PAD_33_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735288254169109/NO_BOOST_PAD_33_USED.replay"],
        "12_AND_100_BOOST_PADS_0_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/496071113768697859/12_AND_100_BOOST_PADS_0_USED.replay"],
        "WASTED_BOOST_WHILE_SUPER_SONIC": [
            "https://cdn.discordapp.com/attachments/493849514680254468/497191273619259393/WASTED_BOOST_WHILE_SUPER_SONIC.replay"],
        "CALCULATE_USED_BOOST_WITH_DEMO": [
            "https://cdn.discordapp.com/attachments/493849514680254468/497189284651204609/CALCULATE_USED_BOOST_WITH_DEMO.replay"],
        "CALCULATE_USED_BOOST_DEMO_WITH_FLIPS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/497189968397991937/CALCULATE_USED_BOOST_DEMO_WITH_FLIPS.replay"],
        "MORE_THAN_100_BOOST": [
            "https://cdn.discordapp.com/attachments/493849514680254468/497190406472204288/MORE_THAN_100_BOOST.replay"],
        "USE_BOOST_AFTER_GOAL": [
            "https://cdn.discordapp.com/attachments/493849514680254468/497190907309850634/USE_BOOST_AFTER_GOAL.replay"
        ],
        "FEATHERING_34x100_BO0ST_USED": [
            "https://cdn.discordapp.com/attachments/493849514680254468/499640872313290763/FEATHERING_34_X_100_BOOSTS_USED.replay"
        ],

        # Kickoffs
        "STRAIGHT_KICKOFF_GOAL": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495735301604376576/Straight_Kickoff_Goal.replay"],
        "KICKOFF_NO_TOUCH": [
            "https://cdn.discordapp.com/attachments/493849514680254468/496034430943756289/NO_KICKOFF.replay"],
        "3_KICKOFFS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/496034443442782208/3_KICKOFFS_4_SHOTS.replay"],

        # hits
        "4_SHOTS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/496034443442782208/3_KICKOFFS_4_SHOTS.replay"],
        "KICKOFF_3_HITS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/496072257928691743/KICKOFF_3_HITS.replay"],
        "MID_AIR_PASS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495887162928267314/MID_AIR_PASS_GOAL.replay"],
        "HIGH_AIR_PASS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495887164425633802/HIGH_AIR_PASS_GOAL.replay"],
        "GROUND_PASS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495887165570678794/GROUNDED_PASS_GOAL.replay"],
        "PINCH_GROUND": [
            "https://cdn.discordapp.com/attachments/493849514680254468/495887167932071947/PINCH_GROUNDED_GOAL.replay"],
        "DEFAULT_3_ON_3_AROUND_58_HITS": [
            "https://cdn.discordapp.com/attachments/493849514680254468/496820586811621387/DEFAULT_3_ON_3_AROUND_58_HITS.replay"],

        # error cases
        "UNICODE_ERROR": [
            "https://cdn.discordapp.com/attachments/493849514680254468/493880540802449462/UnicodeEncodeError.replay"],
    }


def get_specific_replays():
    raw_map = get_raw_replays()
    return {
        # BOOSTS
        "0_BOOST_COLLECTED": raw_map["NO_BOOST_PAD_0_USED"] + raw_map["NO_BOOST_PAD_33_USED"] + raw_map[
            "KICKOFF_NO_TOUCH"],
        "1_SMALL_PAD": raw_map["12_BOOST_PAD_0_USED"] + raw_map["12_BOOST_PAD_45_USED"],
        "1_LARGE_PAD": raw_map["100_BOOST_PAD_0_USED"] + raw_map["100_BOOST_PAD_100_USED"],
        "0_BOOST_USED": raw_map["12_BOOST_PAD_0_USED"] + raw_map["100_BOOST_PAD_0_USED"] + raw_map[
            "NO_BOOST_PAD_0_USED"] + raw_map["KICKOFF_NO_TOUCH"],
        "BOOST_USED": raw_map["12_BOOST_PAD_45_USED"] +
                      raw_map["100_BOOST_PAD_100_USED"] +
                      raw_map["NO_BOOST_PAD_33_USED"] +
                      raw_map["CALCULATE_USED_BOOST_WITH_DEMO"] +
                      raw_map["CALCULATE_USED_BOOST_DEMO_WITH_FLIPS"] +
                      raw_map["USE_BOOST_AFTER_GOAL"] +
                      raw_map["WASTED_BOOST_WHILE_SUPER_SONIC"],
        "BOOST_FEATHERED": raw_map["MORE_THAN_100_BOOST"] + raw_map["FEATHERING_34x100_BO0ST_USED"],
        "BOOST_WASTED_USAGE": raw_map["WASTED_BOOST_WHILE_SUPER_SONIC"],
        "BOOST_WASTED_COLLECTION": raw_map["MORE_THAN_100_BOOST"],
        # HITS
        "HITS": raw_map["4_SHOTS"] + raw_map["KICKOFF_3_HITS"] + raw_map["12_BOOST_PAD_45_USED"] +
                raw_map["MID_AIR_PASS"] + raw_map["HIGH_AIR_PASS"] + raw_map["GROUND_PASS"] +
                raw_map["1_NORMAL_SAVE"] + raw_map["1_EPIC_SAVE"] + raw_map["1_AERIAL"] + raw_map["DEFAULT_3_ON_3_AROUND_58_HITS"],
        # + raw_map["PINCH_GROUND"],  TODO: Fix pinches to create 2 hits 1 for each person on same frame
        "SHOTS": raw_map["4_SHOTS"] + raw_map["12_BOOST_PAD_45_USED"] +
                 raw_map["1_EPIC_SAVE"] + raw_map["1_NORMAL_SAVE"],
        "PASSES": raw_map["MID_AIR_PASS"] + raw_map["HIGH_AIR_PASS"] + raw_map["GROUND_PASS"],
        "AERIALS": raw_map["1_EPIC_SAVE"] + raw_map["1_AERIAL"] + raw_map["HIGH_AIR_PASS"] + raw_map["MID_AIR_PASS"],
    }


def get_specific_answers():
    specific_replays = get_specific_replays()
    return {
        # Boost
        "0_BOOST_USED": [0] * len(specific_replays["0_BOOST_USED"]),
        "BOOST_USED": [45, 100, 33, 33.33 + 33.33 + 12.15, 33.33, 33.33, 0],
        "BOOST_WASTED_USAGE": [33.33],
        "BOOST_WASTED_COLLECTION": [6.2],
        "BOOST_FEATHERED": [100.0, 3490.0],
        # Hits
        "HITS": [4, 3, 1, 2, 9, 2, 4, 4, 4, 50],
        "SHOTS": [3, 0, 2, 1],
        "PASSES": [1, 1, 1],
        "AERIALS": [0, 1, 2, 0]
    }


def assertNearlyEqual(self, a, b, percent=2.0, msg=None):
    if abs(a - b) > abs(percent / 100.0 * min(abs(a), abs(b))):
        if msg is None:
            self.fail("The given numbers %s and %s are not within %s percent of each other."%(a, b, percent))
        else:
            self.fail(msg)
