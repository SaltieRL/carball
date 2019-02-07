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
    _replay_filepaths = get_all_replay_filepaths(r"D:\Replays\temp\neu_b\replays")
    save_replay_data(_replay_filepaths, output_folder=r"D:\Replays\temp\neu_b\decompiled",
                     save_fn=partial(save_description_dict, analysis_folder=r"D:\Replays\temp\neu_b\analysis"))
