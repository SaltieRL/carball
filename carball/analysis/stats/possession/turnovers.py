from typing import Dict

import pandas as pd

from carball.generated.api.stats.events_pb2 import Hit
from ....analysis.constants.field_constants import FieldConstants
from ....analysis.stats.stats import HitStat
from ....generated.api import game_pb2
from ....generated.api.player_pb2 import Player
from ....json_parser.game import Game


class TurnoverStat(HitStat):
    field_constants = FieldConstants()

    def initialize_hit_stat(self, game: Game, player_map: Dict[str, Player], data_frame: pd.DataFrame):
        pass

    def calculate_next_hit_stat(self, game: Game, proto_game: game_pb2.Game, saltie_hit: Hit, next_saltie_hit: Hit,
                                player_map: Dict[str, Player], hit_index: int):
        hits = proto_game.game_stats.hits
        hit_player = player_map[saltie_hit.player_id.id]
        second_hit_player = player_map[next_saltie_hit.player_id.id]

        # If there is a goal between 2nd hit and 3rd hit abort check
        if not next_saltie_hit.HasField("next_hit_frame_number") or hit_index + 2 >= len(hits):
            return

        third_hit_player = player_map[hits[hit_index + 2].player_id.id]
        if hit_player.is_orange != second_hit_player.is_orange and hit_player.is_orange != third_hit_player.is_orange:
            # this is a turnover!
            # if the hit occurred on the on the same half as my team
            my_half = (saltie_hit.ball_data.pos_y > 0) == hit_player.is_orange
            neutral_zone = self.field_constants.get_neutral_zone(saltie_hit.ball_data)
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
