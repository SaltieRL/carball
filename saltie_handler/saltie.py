import os
import subprocess
import json

from game.game import Game
# from analyser.game_analyser import analyse_game
from controls.controls import get_controls


ROCKET_LEAGUE_REPLAY_PARSER_DIR = 'RocketLeagueReplayParser'
ROCKET_LEAGUE_REPLAY_PARSER_EXE = 'RocketLeagueReplayParser.exe'


def create_saltie_replay(file_path):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    print(os.path.join(base_dir, ROCKET_LEAGUE_REPLAY_PARSER_DIR, ROCKET_LEAGUE_REPLAY_PARSER_EXE),
           file_path)
    cmd = [os.path.join(base_dir, ROCKET_LEAGUE_REPLAY_PARSER_DIR, ROCKET_LEAGUE_REPLAY_PARSER_EXE),
           file_path]
    output = subprocess.run(cmd, stdout=subprocess.PIPE)
    # print(output.stdout.decode('UTF-8'))
    _json = json.loads(output.stdout.decode('utf-8'))

    game = Game(loaded_json=_json)
    # print(game.players[0].data.loc[:, ['pos_x', 'pos_y', 'pos_z']].max().values)
    # print(game.players[0].data.loc[:, ['vel_x', 'vel_y', 'vel_z']].max().values)
    # print(game.players[0].data.loc[:, ['rot_x', 'rot_y', 'rot_z']].max().values)
    # print(game.players[0].data.loc[:, ['ang_vel_x', 'ang_vel_y', 'ang_vel_z']].max().values)
    # analyse_game(game)
    get_controls(game)
    return game




if __name__ == '__main__':
    # file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'F32B2B4540BD322CC57756869143B49D.replay')
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '95C06233401FC55A02E4CAAF22375FA9.replay')
    # file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '7.replay')
    create_saltie_replay(file_path)