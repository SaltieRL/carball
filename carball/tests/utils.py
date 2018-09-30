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


def run_tests_on_list(unit_test_func: Callable, replay_list=None):
    if replay_list is None:
        replay_list = get_full_replay_list()

    for replay_url in replay_list:
        run_replay(replay_url, unit_test_func)


def run_replay(url, func: Callable):
    """
    Runs the replay with the file downloaded locally then deletes the file.
    :param url:
    :param func:
    :return:
    """

    replay = download_replay_discord(url)
    file = save_locally(replay)

    fd, file_path = tempfile.mkstemp()
    os.close(fd)
    func(file, file_path)
    os.remove(file)
    os.remove(file_path)


def run_analysis_test_on_replay(unit_test_func: Callable, replay_list=None):
    """
    :param unit_test_func: Called with an AnalysisManager
    :param replay_list: list of replay urls
    :return:
    """
    def wrapper(replay_file_path, json_file_path):
        analysis_manager = analyze_replay_file(replay_file_path, json_file_path)
        unit_test_func(analysis_manager)
    run_tests_on_list(wrapper, replay_list)


def get_full_replay_list():
    """
    For full replays that have crashed or failed to be converted
    :return:
    """
    return ['https://cdn.discordapp.com/attachments/493849514680254468/493880540802449462/UnicodeEncodeError.replay']


def get_specific_replays():
    """
    Partial replays for specific values.
    :return:
    """
    return {
        "0_JUMPS": ["https://cdn.discordapp.com/attachments/493849514680254468/495735116895748096/0_JUMPS.replay"],
        "0_SAVES": ["https://cdn.discordapp.com/attachments/493849514680254468/495735137133264897/0_SAVES.replay"],
        "1_AERIAL": ["https://cdn.discordapp.com/attachments/493849514680254468/495735149133168651/1_AERIAL.replay"],
        "1_DEMO": ["https://cdn.discordapp.com/attachments/493849514680254468/495735163117109249/1_DEMO.replay"],
        "1_DOUBLE_JUMP": ["https://cdn.discordapp.com/attachments/493849514680254468/495735176761049103/1_DOUBLE_JUMP.replay"],
        "1_EPIC_SAVE": ["https://cdn.discordapp.com/attachments/493849514680254468/495735191537713153/1_EPIC_SAVE.replay"],
        "1_JUMP": ["https://cdn.discordapp.com/attachments/493849514680254468/495735203323576321/1_JUMP.replay"],
        "1_NORMAL_SAVE": ["https://cdn.discordapp.com/attachments/493849514680254468/495735215767945234/1_NORMAL_SAVE.replay"],
        "12_BOOST_PAD_0_USED": ["https://cdn.discordapp.com/attachments/493849514680254468/495735228422291456/12_BOOST_PAD_0_USED.replay"],
        "12_BOOST_PAD_45_USED": ["https://cdn.discordapp.com/attachments/493849514680254468/495735240321662986/12_BOOST_PAD_45_USED.replay"],
        "100_BOOST_PAD_0_USED": ["https://cdn.discordapp.com/attachments/493849514680254468/495735252233224193/100_BOOST_PAD_0_USED.replay"],
        "100_BOST_PAD_100_USED": ["https://cdn.discordapp.com/attachments/493849514680254468/495735264262488065/100_BOOST_PAD_100_USED.replay"],
        "NO_BOOST_PAD_0_USED": ["https://cdn.discordapp.com/attachments/493849514680254468/495735276338020372/NO_BOOST_PAD_0_USED.replay"],
        "NO_BOOST_PAD_33_USED": ["https://cdn.discordapp.com/attachments/493849514680254468/495735288254169109/NO_BOOST_PAD_33_USED.replay"],
        "STRAIGHT_KICKOFF_GOAL": ["https://cdn.discordapp.com/attachments/493849514680254468/495735301604376576/Straight_Kickoff_Goal.replay"],
        "KICKOFF_NO_TOUCH": ["https://cdn.discordapp.com/attachments/493849514680254468/496034430943756289/NO_KICKOFF.replay"],
        "3_KICKOFFS": ["https://cdn.discordapp.com/attachments/493849514680254468/496034443442782208/3_KICKOFFS_4_SHOTS.replay"],
        "4_SHOTS": ["https://cdn.discordapp.com/attachments/493849514680254468/496034443442782208/3_KICKOFFS_4_SHOTS.replay"]
    }


