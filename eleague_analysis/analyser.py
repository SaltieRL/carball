import os
import pickle
from collections import defaultdict

import pandas as pd

# ANALYSIS_FOLDER = r"E:\replays\s6analysis"
ANALYSIS_FOLDER = r"E:\replays\s6leagueplay\analysis"
# ANALYSIS_FOLDER = r"E:\replays\s6euleagueplay\analysis"

player_name_alternates_s6 = {
    "Daze~": "Daze",
    'Kronovi ^-^': 'G2 Kronovi ^-^',
    'Kro': 'G2 Kronovi ^-^',
    'JKnaps': 'G2 JKnaps',
    'Leth': 'Lethamyr',
    'Markydooda (as seen in pic)': 'Markydooda',
    'Markydooda (pic related)': 'Markydooda',
    'NRG jstn. :D': 'jstn.',
    'jstn. ツ': 'jstn.',
    'blu3y': 'Bluey.',
    'chrome': 'Chrome',
    'delusion': 'Delusion',
    'hato': 'Hato',
    'malakiss': 'MALAKISS',
    'Maestro.': 'Maestro',
    'timi': "Timi",
    'yeatzy_': 'yeatzy',
    'OoS.EPICJonny': 'EPICJonny'
}
player_name_alternates = {
    'Kro': 'Kronovi ^-^',
    'jstn. ツ': 'jstn.',
    'Leth': 'Lethamyr',
}


#
# teams = {
#     'WDG': ['remkoe', 'EyeIgnite', 'Metsanauris'],
#     'PSG': ['Chausette45', 'Ferra', 'fruity'],
#     'NRG': ['Fireburner', 'GarrettG', 'jstn. ツ'],
#     'F3': ['Yukeo', 'kuxir97', 'miztik'],
#     'EG': ['CorruptedG', 'klassux', 'Chicago'],
#     'DIG': ['Kaydop', 'Turbopolsa', 'ViolentPanda'],
#     'C9': ['Squishy', 'Torment', 'Gimmick'],
#     'CHF': ['Kamii', 'Torsos', 'Drippay'],
# }

# player_to_team = {}
# for _team, _players in teams.items():
#     for _player in _players:
#         player_to_team[_player] = _team


def analyse():
    description_dict_paths = []
    for root, dirs, files in os.walk(ANALYSIS_FOLDER):
        for file in files:
            # print(root, file)
            filepath = os.path.join(root, file)
            description_dict_paths.append(filepath)

    description_dicts = []
    for description_dict_path in description_dict_paths:
        with open(description_dict_path, 'rb') as f:
            description_dict = pickle.load(f)
            description_dicts.append(description_dict)

    # Rename players from alternate names
    for description_dict in description_dicts:
        description_dict['defenders'] = [[player_name_alternates.get(player_, player_) for player_ in list_]for list_ in description_dict['defenders']]
        description_dict['shooter'] = [player_name_alternates.get(player_, player_) for player_ in description_dict['shooter']]
        description_dict['saves'] = [player_name_alternates.get(player_, player_) for player_ in description_dict['saves']]

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
        "matches": matches,
        "goals": goals,
        "goal_per_xG": goal_per_xG,
        "average_xG_per_shot": average_xG_per_shot,
        "xG_per_match": xG_per_match,
        "goals_against": goals_against,
        "goal_against_per_xGa": goal_against_per_xGa,
        "average_xGa_per_defence": average_xGa_per_defence,
        "xGa_per_match": xGa_per_match,
    }
    xG_df = pd.DataFrame.from_dict(data_dict)
    # xG_df.to_csv(filename)
    pass


if __name__ == '__main__':
    analyse()
