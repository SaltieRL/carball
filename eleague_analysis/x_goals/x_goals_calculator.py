import numpy as np
import pandas as pd
from tensorflow.python.keras.models import load_model

from carball.analysis.constants.basic_math import get_distance_from_displacements, get_player_ball_displacements
from carball.generated.api.game_pb2 import Game
from eleague_analysis.utils.utils import normalise_df, flip_teams
from eleague_analysis.x_goals.x_goals import get_input_and_output_from_game_datas

MODEL = load_model(r'C:\Users\harry\Documents\rocket_league\carball\eleague_analysis\x_goals\x_goals.876-0.76482.hdf5')


def calculate_x_goals_prediction(df: pd.DataFrame, proto: Game):
    normalised_df = normalise_df(df)
    input_, output, hits_order = get_input_and_output_from_game_datas(normalised_df, proto)
    input_2, output_2, hits_order2 = get_input_and_output_from_game_datas(normalised_df, proto, filter_shots_only=False)

    predicted_x_goals = MODEL.predict(input_)
    predicted_x_goals_2 = MODEL.predict(input_2)

    defenders = find_shooters_and_defenders(df, proto)
    # pd.DataFrame.from_dict({'is_goal': output.flatten(), 'predicted_xG': predicted_x_goals.flatten(),
    #                         'frame': [_ for _ in defenders.keys()], 'seconds': [300 - _[1] for _ in defenders.values()],
    #                         'defenders': [_[1:] for _ in defenders.values()],
    #                         'shooter': [_[0] for _ in defenders.values()]}, orient='columns')
    description_dict = {'is_goal': output.flatten(),
                        'predicted_xG': predicted_x_goals.flatten(),
                        'frame': [_ for _ in defenders.keys()],
                        'seconds': [300 - _[1] for _ in defenders.values()],
                        'defenders': [_[2:] for _ in defenders.values()],
                        'shooter': [_[0] for _ in defenders.values()],
                        'saves': [None for _ in range(len(output.flatten()))]}
    hits = proto.game_stats.hits
    shots = [hit for hit in hits if hit.shot]

    player_id_to_player = {
        player.id.id: player
        for player in proto.players
    }
    for i, hit in enumerate(hits):
        if hit.save:
            shot = hits[i - 1]
            index = shots.index(shot)
            description_dict['saves'][index] = hit.player_id.id, player_id_to_player[hit.player_id.id].name

    # pd.DataFrame.from_dict(description_dict)
    pass
    return description_dict


def find_shooters_and_defenders(df: pd.DataFrame, proto: Game):
    name_team_map = {player.name: player.is_orange for player in proto.players}
    player_id_to_player = {
        player.id.id: player
        for player in proto.players
    }
    teams = {
        0: [player for player in proto.players if not player.is_orange],
        1: [player for player in proto.players if player.is_orange]
    }

    df_orange = flip_teams(df)

    hits = proto.game_stats.hits

    hit_frame_numbers = np.array([hit.frame_number for hit in hits if hit.shot])

    hit_frames = df.loc[hit_frame_numbers, (slice(None), ['pos_x', 'pos_y', 'pos_z'])]

    # player_names = [name for name in df.columns.levels[0].values if name != 'ball' and name != 'game']
    #
    # player_displacements = {player_name: get_player_ball_displacements(hit_frames, player_name)
    #                             for player_name in player_names}
    # player_distances = {player_name: get_distance_from_displacements(data_frame).rename(player_name)
    #                     for player_name, data_frame in player_displacements.items()}
    #
    # player_distances_data_frame = pd.concat(player_distances, axis=1)

    hit_defenders = {}  # Hit: [shooter, defenders]
    for hit in hits:
        if not hit.shot:
            continue
        shooter = player_id_to_player[hit.player_id.id]
        # SET DEFENDER TO ORANGE TEAM
        if shooter.is_orange:
            _df = df_orange
        else:
            _df = df

        # Find defenders behind ball
        defending_team = teams[0 if shooter.is_orange else 1]

        # hit_defenders[hit.frame_number] = [shooter.name, _df.loc[hit.frame_number, ('game', 'seconds_remaining')]]
        hit_defenders[hit.frame_number] = [(shooter.id.id, shooter.name), _df.loc[hit.frame_number, ('game', 'seconds_remaining')]]
        for defender in defending_team:
            ball_y = _df.loc[hit.frame_number, ('ball', 'pos_y')]
            defender_y = _df.loc[hit.frame_number, (defender.name, 'pos_y')]
            ball_x = _df.loc[hit.frame_number, ('ball', 'pos_x')]
            defender_x = _df.loc[hit.frame_number, (defender.name, 'pos_x')]
            if defender_y > ball_y and (
                    abs(defender_x) < 900 or (-800 < defender_x < ball_x) or (ball_x < defender_x < 800)):
                hit_defenders[hit.frame_number].append((defender.id.id, defender.name))
    return hit_defenders
