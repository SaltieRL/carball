import logging
from typing import Dict

import pandas as pd
import numpy as np

from carball.analysis.stats.stats import BaseStat
from carball.generated.api.player_pb2 import Player
from carball.generated.api import game_pb2
from carball.json_parser.game import Game
from carball.analysis.stats.dropshot import is_dropshot

log = logging.getLogger(__name__)


class DropshotBallPhaseTimes(BaseStat):
    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game, player_map: Dict[str, Player],
                       data_frame: pd.DataFrame):
        if not is_dropshot(game):
            return

        phase_air_times = [[], [], []]

        all_events = list(map(lambda x: (x['frame_number'], x['state']), game.dropshot['ball_events']))
        all_events.extend(map(lambda x: (x['frame_number'], 0), game.dropshot['damage_events']))
        all_events.sort(key=lambda x: x[0])

        current_frame = data_frame['ball'].index[0]
        current_phase = 0

        for ball_event in all_events:
            if ball_event[1] == current_phase:
                continue

            phase_time = data_frame['game', 'time'].loc[ball_event[0]] - data_frame['game', 'time'].loc[current_frame]
            phase_air_times[current_phase].append(phase_time)

            current_frame = ball_event[0]
            current_phase = ball_event[1]

        # last phase
        phase_time = data_frame['game', 'time'].iloc[-1] - data_frame['game', 'time'].loc[current_frame]
        phase_air_times[current_phase].append(phase_time)

        for phase, times in enumerate(phase_air_times):
            phase_stat_proto = proto_game.game_stats.ball_stats.extra_mode.dropshot_phase_stats.add()
            phase_stat_proto.phase = phase
            if len(times) > 0:
                phase_stat_proto.average = np.mean(times)
                phase_stat_proto.max = max(times)
                phase_stat_proto.total = sum(times)
            else:
                phase_stat_proto.average = 0
                phase_stat_proto.max = 0
                phase_stat_proto.total = 0
