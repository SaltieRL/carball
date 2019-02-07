import os
import pickle
from collections import defaultdict

import pandas as pd
names = defaultdict(lambda: [])
players_to_analyse = ['76561198060924319', '76561198176496186', "76561198055442516"]

def rename_scheme(player_id: str, player_name: str) -> str:
    # if player_id not in players_to_analyse:
    #     player_id = "other"

    if player_name not in names[player_id]:
        names[player_id].append(player_name)
    return player_id


def analyse(analysis_folder: str):
    description_dict_paths = []
    for root, dirs, files in os.walk(analysis_folder):
        for file in files:
            # print(root, file)
            filepath = os.path.join(root, file)
            description_dict_paths.append(filepath)

    description_dicts = []
    for description_dict_path in description_dict_paths:
        with open(description_dict_path, 'rb') as f:
            description_dict = pickle.load(f)
            description_dicts.append(description_dict)

    # # Rename players from alternate names
    for description_dict in description_dicts:
        description_dict['defenders'] = [[rename_scheme(player_id, player_name) for player_id, player_name in list_]for list_ in description_dict['defenders']]
        description_dict['shooter'] = [rename_scheme(player_id, player_name) for player_id, player_name in description_dict['shooter']]
        description_dict['saves'] = [rename_scheme(player_or_none[0], player_or_none[1]) if player_or_none is not None else None for player_or_none in description_dict['saves']]

    # Count matches
    matches = defaultdict(lambda: 0)
    for description_dict in description_dicts:
        players = set()
        for defenders in description_dict['defenders']:
            players.update(defenders)
        players.update(description_dict['shooter'])
        players.update(description_dict['saves'])
        try:
            players.remove(None)
        except KeyError:
            pass
        for player in players:
            matches[player] += 1

    dfs = [pd.DataFrame.from_dict(description_dict) for description_dict in description_dicts]

    full_df = pd.concat(dfs)

    # xGs = {
    #     player: [[], 0]  # xGs, goals
    #     for player in player_to_team.keys()
    # }

    # xGas = {
    #     player: [[], 0]  # xGa, goals against
    #     for player in player_to_team.keys()
    # }

    xGs = defaultdict(lambda: [[], 0])
    xGas = defaultdict(lambda: [[], 0])

    for row in full_df.itertuples():
        if row.predicted_xG < 0.01:
            continue
        xGs[row.shooter][0].append(row.predicted_xG)
        if row.is_goal:
            xGs[row.shooter][1] += 1

        _defenders = set([defender for defender in row.defenders] + [row.saves])
        try:
            _defenders.remove(None)
        except KeyError:
            pass
        for defender in _defenders:
            xGas[defender][0].append(row.predicted_xG)
            if row.is_goal:
                xGas[defender][1] += 1

    goal_per_xG = {player: _xGs[1] / sum(_xGs[0]) for player, _xGs in xGs.items()}
    average_xG_per_shot = {player: sum(_xGs[0]) / len(_xGs[0]) for player, _xGs in xGs.items()}
    xG_per_match = {player: sum(_xGs[0]) / matches[player] for player, _xGs in xGs.items()}

    goal_against_per_xGa = {player: _xGas[1] / sum(_xGas[0]) for player, _xGas in xGas.items()}
    average_xGa_per_defence = {player: sum(_xGas[0]) / len(_xGas[0]) for player, _xGas in xGas.items()}
    xGa_per_match = {player: sum(_xGas[0]) / matches[player] for player, _xGas in xGas.items()}

    goals = {player: _xGs[1] for player, _xGs in xGs.items()}
    goals_against = {player: _xGas[1] for player, _xGas in xGas.items()}
    data_dict = {
        "first_name":  {player_id: names_[0] for player_id, names_ in names.items()},
        "matches": matches,
        "goals": goals,
        "goal_per_xG": goal_per_xG,
        "average_xG_per_shot": average_xG_per_shot,
        "xG_per_match": xG_per_match,
        "goals_against": goals_against,
        "goal_against_per_xGa": goal_against_per_xGa,
        "average_xGa_per_defence": average_xGa_per_defence,
        "xGa_per_match": xGa_per_match,
        "names": names
    }
    xG_df = pd.DataFrame.from_dict(data_dict)
    xG_df.dropna().to_csv('xG_df.csv')
    pass


if __name__ == '__main__':
    analyse(analysis_folder=r"D:\Replays\temp\neu_b\analysis")
