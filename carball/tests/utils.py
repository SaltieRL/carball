import os
import tempfile
from typing import Callable

import requests


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


def test_on_list(unit_test, replay_list=None):
    if replay_list is None:
        replay_list = get_replay_list()

    for replay_url in replay_list:
        run_replay(replay_url, unit_test)


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


def get_replay_list():
    return ['https://cdn.discordapp.com/attachments/493849514680254468/493880540802449462/UnicodeEncodeError.replay']
