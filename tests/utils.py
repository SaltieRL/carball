import os
import tempfile

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

def run_replay(url):
    replay = download_replay_discord(url)
    file = save_locally(replay)



if __name__ == "__main__":
    replay = download_replay_discord('https://cdn.discordapp.com/attachments/493849514680254468/493880540802449462/UnicodeEncodeError.replay')
    save_locally(replay)
