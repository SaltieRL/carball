from typing import Callable
from replay_analysis.generated.api import player_pb2
from replay_analysis.json_parser.player import Player
from .ApiPlayerCameraSettings import ApiPlayerCameraSettings
from .ApiPlayerLoadout import ApiPlayerLoadout


class ApiPlayer:

    @staticmethod
    def create_from_player(proto_player: player_pb2.Player, player: Player, id_creator: Callable):
        ApiPlayerCameraSettings.create_from_player(proto_player.camera_settings, player)
        ApiPlayerLoadout.create_from_player(proto_player.loadout, player)

        id_creator(proto_player.id, player.name)
        proto_player.name = player.name
        if player.title is not None:
            proto_player.title_id = player.title
        proto_player.score = player.score
        proto_player.goals = player.goals
        proto_player.assists = player.assists
        proto_player.saves = player.saves
        proto_player.shots = player.shots
        proto_player.is_orange = player.is_orange

        return proto_player
