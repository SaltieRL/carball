from typing import Dict

import pandas as pd

from ....analysis.constants.field_constants import FieldConstants
from ....analysis.stats.stats import BaseStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....json_parser.game import Game


class TurnoverStat(BaseStat):

    field_constants = FieldConstants()

    def calculate_stat(self, proto_stat, game: Game, proto_game: game_pb2.Game,
                       player_map: Dict[str, Player], data_frame: pd.DataFrame):

        hits = list(proto_stat.hits)
        for i in range(len(hits) - 2):
            hit_player = player_map[hits[i].player_id.id]
            second_hit_player = player_map[hits[i + 1].player_id.id]
            third_hit_player = player_map[hits[i + 2].player_id.id]
            if hit_player.is_orange != second_hit_player.is_orange:
                if third_hit_player.is_orange != second_hit_player.is_orange:
                    # this is a turnover!
                    # if the hit occurred on the on the same half as my team
                    my_half = (hits[i].ball_data.pos_y > 0) == hit_player.is_orange
                    neutral_zone = self.field_constants.get_neutral_zone(hits[i].ball_data)
                    self.assign_turnover(hit_player.stats.possession, my_half, neutral_zone)
                    self.assign_turnover(proto_game.teams[hit_player.is_orange].stats.possession,
                                         my_half, neutral_zone)
                    second_hit_player.stats.possession.won_turnovers += 1
                    proto_game.teams[second_hit_player.is_orange].stats.possession.won_turnovers += 1

    def assign_turnover(self, possession_proto, is_turnover_my_half, is_neutral):
        possession_proto.turnovers += 1
        if is_turnover_my_half and not is_neutral:
            possession_proto.turnovers_on_my_half += 1
        elif not is_neutral:
            possession_proto.turnovers_on_their_half += 1
