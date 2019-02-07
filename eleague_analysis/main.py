import os
import pickle
from typing import List, Sequence

import carball
from eleague_analysis.x_goals.x_goals_calculator import calculate_x_goals_prediction

# REPLAY_FOLDER = r"E:\replays\ELEAGUE Cup_ Rocket League 2018"
# OUTPUT_FOLDER = r"E:\replays\decompiled"
# ANALYSIS_FOLDER = r"E:\replays\analysis"

# REPLAY_FOLDER = r"E:\replays\RLCS Season 5"
# OUTPUT_FOLDER = r"E:\replays\s5decompiled"
# ANALYSIS_FOLDER = r"E:\replays\s5analysis"

# REPLAY_FOLDER = r"E:\replays\RLCS Season 6"
# OUTPUT_FOLDER = r"E:\replays\s6decompiled"
# ANALYSIS_FOLDER = r"E:\replays\s6analysis"

# REPLAY_FOLDER = r"E:\replays\RLCS Season 6\RLCS\RLCS NA League Play"
# OUTPUT_FOLDER = r"E:\replays\s6leagueplay\decompiled"
# ANALYSIS_FOLDER = r"E:\replays\s6leagueplay\analysis"

# REPLAY_FOLDER = r"E:\replays\RLCS Season 6\RLCS\RLCS EU League Play"
# OUTPUT_FOLDER = r"E:\replays\s6euleagueplay\decompiled"
# ANALYSIS_FOLDER = r"E:\replays\s6euleagueplay\analysis"

# REPLAY_FOLDER = r"E:\replays\RLCS Season 6\RLCS\RLCS EU League Play"
REPLAY_FOLDER = r"E:\replays\RLCS Season 6\RLCS\RLCS NA League Play"
OUTPUT_FOLDER = r"E:\replays\s6euleagueplay\decompiled"
POSSESSIONS_FOLDER = r"E:\replays\s6leagueplay\possessions"


def get_all_replay_filepaths() -> List[str]:
    replay_filepaths = []

    for root, dirs, files in os.walk(REPLAY_FOLDER):
        for file in files:
            # print(root, file)
            if file.endswith('.replay'):
                _replay_filepaths = os.path.join(root, file)
                replay_filepaths.append(_replay_filepaths)

    print(f"Found {len(replay_filepaths)} replay files.")
    return replay_filepaths


def analyse_replays(replay_filepaths: Sequence[str]):
    # filepath_to_start_from = r"E:\replays\RLCS Season 5\RLCS OCE League Play\Week 4\Legs are Silly vs. JAM\4.replay"
    filepath_to_start_from = None
    skip = False
    for replay_filepath in replay_filepaths:
        try:
            if skip:
                if replay_filepath != filepath_to_start_from:
                    print(f"Skipping {replay_filepath}")
                    continue
                else:
                    skip = False
            print(replay_filepath)

            replay_filename = os.path.basename(replay_filepath)[:-7]
            output_path = os.path.join(OUTPUT_FOLDER, replay_filename) + ".json"
            analysis = carball.analyze_replay_file(replay_filepath, output_path=output_path)
            df = analysis.data_frame
            game = analysis.game
            proto_game = analysis.protobuf_game

            # Move decompiled file if game.id is not replay_filename
            if game.id != replay_filename:
                new_output_path = os.path.join(OUTPUT_FOLDER, game.id) + ".json"
                try:
                    os.rename(output_path, new_output_path)
                except FileExistsError:
                    pass

            # save_description_dict(df, game, proto_game)
            save_possessions(df, game, proto_game)

        except:
            import traceback
            with open('errors.txt', 'a') as f:
                f.write(replay_filepath + '\nTraceback:\n' + traceback.format_exc() + '\n')
        pass


def save_description_dict(df, game, proto_game):
    description_dict = calculate_x_goals_prediction(df, proto_game)
    analysis_path = os.path.join(ANALYSIS_FOLDER, game.id) + '.pkl'
    with open(analysis_path, 'wb') as f:
        pickle.dump(description_dict, f, protocol=pickle.HIGHEST_PROTOCOL)


def save_possessions(df, game, proto_game):
    possessions = {
        "player_possessions_dict": game.player_possessions_dict,
        "player_possession_stats_dict": game.player_possession_stats_dict,
        "team_possessions_dict": game.team_possessions_dict,
        "team_possession_stats_dict": game.team_possession_stats_dict,
    }
    # Convert to pickle-able
    for key in ["player_possessions_dict", "team_possessions_dict"]:
        dict_ = possessions[key]
        for player_or_team, possessions_list in dict_.items():
            for possession_ in possessions_list:
                # possessions["player_possessions_dict"]['76561198030080604'][0].hits[0].SerializeToString()
                possession_.hits = [hit.SerializeToString() for hit in possession_.hits]

    analysis_path = os.path.join(POSSESSIONS_FOLDER, game.id) + '.pkl'
    with open(analysis_path, 'wb') as f:
        pickle.dump(possessions, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    replay_filepaths = get_all_replay_filepaths()
    analyse_replays(replay_filepaths)
