import os
import pickle
from collections import Counter
from functools import partial
from typing import Sequence, List, Callable

import pandas as pd
import requests

import carball
from carball.generated.api.game_pb2 import Game
from carball.json_parser.game import Game as JsonParserGame
from eleague_analysis.x_goals.x_goals_calculator import calculate_x_goals_prediction

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


def get_all_replay_filepaths(folder: str) -> List[str]:
    replay_filepaths = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            # print(root, file)
            if file.endswith('.replay'):
                _replay_filepaths = os.path.join(root, file)
                replay_filepaths.append(_replay_filepaths)

    print(f"Found {len(replay_filepaths)} replay files.")
    return replay_filepaths


def save_replay_data(replay_filepaths: Sequence[str], save_fn: Callable[[pd.DataFrame, JsonParserGame, Game], None],
                     output_folder: str):
    for replay_filepath in replay_filepaths:
        try:
            print(replay_filepath)

            replay_filename = os.path.basename(replay_filepath)[:-7]
            output_path = os.path.join(output_folder, replay_filename) + ".json"
            analysis = carball.analyze_replay_file(replay_filepath, output_path=output_path)
            df = analysis.data_frame
            game = analysis.game
            proto_game = analysis.protobuf_game

            # Move decompiled file if game.id is not replay_filename
            if game.id != replay_filename:
                new_output_path = os.path.join(output_folder, game.id) + ".json"
                try:
                    os.rename(output_path, new_output_path)
                except FileExistsError:
                    pass

            save_fn(df, game, proto_game)

        except:
            import traceback
            with open('errors.txt', 'a') as f:
                f.write(replay_filepath + '\nTraceback:\n' + traceback.format_exc() + '\n')


def save_description_dict(df, game, proto_game, analysis_folder: str):
    description_dict = calculate_x_goals_prediction(df, proto_game)
    analysis_path = os.path.join(analysis_folder, game.id) + '.pkl'
    with open(analysis_path, 'wb') as f:
        pickle.dump(description_dict, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    # _team_replays = get_replays(team_b_ids)
    # download_replays(_team_replays)
    _replay_filepaths = get_all_replay_filepaths(r"D:\Replays\temp\neu_b\replays")
    save_replay_data(_replay_filepaths, output_folder=r"D:\Replays\temp\neu_b\decompiled",
                     save_fn=partial(save_description_dict, analysis_folder=r"D:\Replays\temp\neu_b\analysis"))
