from collections import Counter
from typing import Sequence

import requests

team_a_ids = [
    "76561198121973642",
    "76561198153688415",
    "76561198054151612",
]
team_b_ids = [
    "76561198055442516",
    "76561198060924319",
    "76561198176496186",
]


def get_replays(player_ids: Sequence[str]):
    base_url = "https://calculated.gg/api/replay"

    r = requests.get(base_url, params={'player_ids': player_ids, 'page': 0, 'limit': 200})
    r.raise_for_status()

    r_json = r.json()

    replays = r_json['replays']

    game_modes = Counter([replay['gameMode'] for replay in replays])

    team_replays = []
    for replay in replays:
        players = replay['players']
        team_is_oranges = []
        for player in players:
            if player['id'] in player_ids:
                team_is_oranges.append(player['isOrange'])

        assert len(team_is_oranges) == 3

        if team_is_oranges[0] == team_is_oranges[1] and team_is_oranges[0] == team_is_oranges[2]:
            team_replays.append(replay)

    print(f"Found {len(replays)} total replays, {len(team_replays)} with players on the same team. ")
    return team_replays


def download_replays(replays):
    for replay in replays:
        replay_id = replay['id']
        url = f"https://calculated.gg/api/replay/{replay_id}/download"
        r = requests.get(url)
        with open(rf'D:\Replays\temp\{replay_id}.replay', 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    _team_replays = get_replays(team_b_ids)
    download_replays(_team_replays)
